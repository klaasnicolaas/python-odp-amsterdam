"""Models for Open Data Platform of Amsterdam."""

from __future__ import annotations

import enum
import json
import math
import re
from dataclasses import dataclass
from datetime import UTC, date, datetime
from typing import Any

from .const import FILTER_UNKNOWN
from .exceptions import ODPAmsterdamError


@dataclass
class ParkingSpot:
    """Object representing an ParkingSpot model response from the API."""

    spot_id: str
    spot_type: str | None
    spot_description: str | None

    street: str | None
    number: int | float | None
    orientation: str | None

    coordinates: list[list[float]]
    geometry: dict[str, Any]
    regimes: list[dict[str, Any]]
    version_date: date | None

    @classmethod
    def from_json(cls: type[ParkingSpot], data: dict[str, Any]) -> ParkingSpot:
        """Return ParkingSpot object from a dictionary.

        Args:
        ----
            data: The JSON data from the API.

        Returns:
        -------
            An ParkingSpot object.

        """
        attr = data["properties"]
        regimes = attr["regimes"]
        if not isinstance(attr["id"], str) or not attr["id"].strip():
            msg = "Parking location has no valid source ID"
            raise ODPAmsterdamError(msg)
        number = attr["aantal"]
        if number is not None and (
            isinstance(number, bool)
            or not isinstance(number, (int, float))
            or not math.isfinite(number)
        ):
            msg = "Parking capacity must be a finite number or null"
            raise ODPAmsterdamError(msg)
        if not isinstance(regimes, list) or any(
            not isinstance(regime, dict) for regime in regimes
        ):
            msg = "Parking regimes must be a list of objects"
            raise ODPAmsterdamError(msg)
        raw_date = attr.get("versiedatum")
        try:
            version_date = (
                date.fromisoformat(raw_date) if raw_date is not None else None
            )
        except (TypeError, ValueError) as exception:
            msg = "Parking dataset validity date must be an ISO date or null"
            raise ODPAmsterdamError(msg) from exception
        return cls(
            spot_id=attr["id"],
            spot_type=attr["eType"] or None,
            spot_description=(regimes[0].get("eTypeDescription") or None)
            if regimes
            else None,
            street=filter_unknown(attr["straatnaam"]),
            number=number,
            orientation=filter_unknown(attr["type"]),
            coordinates=data["geometry"]["coordinates"][0],
            geometry=data["geometry"],
            regimes=regimes,
            version_date=version_date,
        )


@dataclass
class ParkingLocations:
    """Retrieved parking records and the source's selection total.

    Completeness means all reported records were retrieved, not an atomic
    source snapshot or verified coverage of every real parking location.
    """

    records: list[ParkingSpot]
    total_count: int
    pages_fetched: int

    @property
    def complete(self) -> bool:
        """Whether the received unique records cover the reported selection."""
        return len(self.records) == self.total_count


class VehicleType(enum.StrEnum):
    """Enumeration representing the vehicle type."""

    BICYCLE = "bicycle"
    CAR = "car"
    TOURINGCAR = "touringcar"


class GarageCategory(enum.StrEnum):
    """Enumeration representing the garage category."""

    GARAGE = "garage"
    PARK_AND_RIDE = "park_and_ride"


class GarageStatus(enum.StrEnum):
    """What the operator reports, next to the free space count.

    Some P+R sites only report open or full without counts, and a closed
    facility reports zero free spaces, so zero alone does not mean full.
    """

    COUNTING = "counting"
    OPEN = "open"
    FULL = "full"
    CLOSED = "closed"
    MALFUNCTION = "malfunction"


GARAGE_STATUSES = {
    "GETAL": GarageStatus.COUNTING,
    "VRIJ": GarageStatus.OPEN,
    "VOL": GarageStatus.FULL,
    "GESLOTEN": GarageStatus.CLOSED,
    "STORING_DEFAULT": GarageStatus.MALFUNCTION,
}


@dataclass
class Garage:
    """Object representing an Garage model response from the API."""

    garage_id: str
    garage_name: str
    vehicle: VehicleType
    category: GarageCategory
    state: str

    free_space_short: int | None
    free_space_long: int | None
    short_capacity: int | None
    long_capacity: int | None
    availability_pct: float | None

    longitude: float
    latitude: float
    updated_at: datetime
    source_name: str | None = None
    status: GarageStatus | None = None

    @classmethod
    def from_json(cls: type[Garage], data: dict[str, Any]) -> Garage:
        """Return Garage object from a dictionary.

        Args:
        ----
            data: The JSON data from the API.

        Returns:
        -------
            An Garage object.

        """
        latitude, longitude = split_coordinates(
            json.dumps(data["geometry"]["coordinates"])
        )
        attr = data["properties"]
        return cls(
            garage_id=data["Id"],
            garage_name=correct_name(attr["Name"]),
            source_name=attr["Name"],
            vehicle=get_vehicle_type(attr["Name"]),
            category=get_category(attr["Name"]),
            state=attr.get("State"),
            # Unknown future values stay None instead of failing the whole feed.
            status=GARAGE_STATUSES.get(attr.get("Status")),
            free_space_short=parse_int(attr["FreeSpaceShort"]),
            free_space_long=parse_int(attr["FreeSpaceLong"]),
            short_capacity=parse_int(attr["ShortCapacity"]),
            long_capacity=parse_int(attr["LongCapacity"]),
            availability_pct=calculate_pct(
                parse_int(attr.get("FreeSpaceShort")),
                parse_int(attr.get("ShortCapacity")),
            ),
            longitude=longitude,
            latitude=latitude,
            updated_at=datetime.strptime(
                attr["PubDate"],
                "%Y-%m-%dT%H:%M:%SZ",
            ).replace(tzinfo=UTC),
        )


def split_coordinates(data: str) -> tuple[float, float]:
    """Split the coordinate data in separate variables.

    Args:
    ----
        data: The data to be split.

    Returns:
    -------
        The coordinates.

    """
    coordinates = json.loads(data)
    if (
        not isinstance(coordinates, list)
        or len(coordinates) != 2
        or any(
            isinstance(value, bool)
            or not isinstance(value, (int, float))
            or not math.isfinite(value)
            for value in coordinates
        )
    ):
        msg = "Invalid garage coordinates"
        raise ValueError(msg)
    first, second = coordinates
    # The provider has used both axis orders; Dutch bounds disambiguate them.
    if 50 <= first <= 54 and 3 <= second <= 8:
        return float(first), float(second)
    if 3 <= first <= 8 and 50 <= second <= 54:
        return float(second), float(first)
    msg = "Garage coordinates are outside the source region"
    raise ValueError(msg)


def parse_int(data: str) -> int | None:
    """Try to parse a string to int, return None if not possible."""
    return None if not data or not data.strip().isdigit() else int(data)


def calculate_pct(
    current: int | None,
    total: int | None,
) -> float | None:
    """Calculate the percentage of free parking spots.

    Args:
    ----
        current: The current amount of free parking spots.
        total: The total amount of parking spots.

    Returns:
    -------
        The percentage of free parking spots.

    """
    if current is None or total is None or total == 0:
        return None
    return round(int(current) / int(total) * 100, 1)


def get_category(name: str) -> GarageCategory:
    """Get the category from the garage name.

    Args:
    ----
        name: The name of the parking garage.

    Returns:
    -------
        The category name.

    """
    if "P+R" in name or re.match(r"PR-\d+_", name.strip()):
        return GarageCategory.PARK_AND_RIDE
    return GarageCategory.GARAGE


def get_vehicle_type(name: str) -> VehicleType:
    """Get the vehicle type from the garage name.

    Args:
    ----
        name: The name of the parking garage.

    Returns:
    -------
        The vehicle type.

    """
    if re.search(r"(?:^|[-_ ])FP(?:[-_ ]|\d)", name):
        return VehicleType.BICYCLE
    if "PT" in name:
        return VehicleType.TOURINGCAR
    return VehicleType.CAR


def correct_name(name: str) -> str:
    """Change parking garage name for consistency if needed.

    Args:
    ----
        name: The name of the parking garage.

    Returns:
    -------
        The corrected name.

    """
    category = get_category(name)
    name = re.sub(r"^(?:P|PR|FP|PT)-\d+_\s*", "", name.strip())
    name = re.sub(
        r"^(?:CE-|ZD-|ZO-|ZU-|DP-|AM-|FJ212P34 |VRN-FJ212|GRV020HNK )", "", name
    )
    name = re.sub(r"\s*\(opendata\)\s*$", "", name, flags=re.IGNORECASE)
    name = " ".join(name.split())
    trailing_number = re.fullmatch(r"(.+) (P(\d+))", name)
    if trailing_number:
        prefix = re.fullmatch(r"P(\d+) (.+)", trailing_number[1])
        if prefix is None:
            name = f"{trailing_number[2]} {trailing_number[1]}"
        elif int(prefix[1]) == int(trailing_number[3]):
            name = f"{trailing_number[2]} {prefix[2]}"
    if category == GarageCategory.PARK_AND_RIDE and "P+R" not in name:
        return f"P+R {name}"
    return name


def filter_unknown(data: str) -> str | None:
    """Filter unknown values from the data."""
    if data in FILTER_UNKNOWN:
        return None
    return data
