"""Models for Open Data Platform of Amsterdam."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from enum import Enum
from typing import Any

from .const import CORRECTIONS, FILTER_NAMES, FILTER_UNKNOWN


@dataclass
class ParkingSpot:
    """Object representing an ParkingSpot model response from the API."""

    spot_id: str
    spot_type: str | None
    spot_description: str | None

    street: str | None
    number: int | None
    orientation: str | None

    coordinates: list[float]

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
        regimes = attr["regimes"][0]
        return cls(
            spot_id=attr["id"],
            spot_type=attr["eType"] or None,
            spot_description=regimes["eTypeDescription"] or None,
            street=filter_unknown(attr["straatnaam"]),
            number=int(attr["aantal"]),
            orientation=filter_unknown(attr["type"]),
            coordinates=data["geometry"]["coordinates"][0],
        )


class VehicleType(str, Enum):
    """Enumeration representing the vehicle type."""

    BICYCLE = "bicycle"
    CAR = "car"
    TOURINGCAR = "touringcar"


class GarageCategory(str, Enum):
    """Enumeration representing the garage category."""

    GARAGE = "garage"
    PARK_AND_RIDE = "park_and_ride"


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
        latitude, longitude = split_coordinates(str(data["geometry"]["coordinates"]))
        attr = data["properties"]
        return cls(
            garage_id=data["Id"],
            garage_name=correct_name(attr["Name"]),
            vehicle=get_vehicle_type(attr["Name"]),
            category=get_category(attr["Name"]),
            state=attr.get("State"),
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
    longitude, latitude = data.split(", ")
    longitude = longitude.replace("[", "")
    latitude = latitude.replace("]", "")
    return float(latitude), float(longitude)


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
    if "P+R" in name:
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
    if "-FP" in name:
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
    for value in FILTER_NAMES:
        # Remove parts from name string.
        name = name.replace(value, "")

    if "PR" in name:
        # Replace PR for P in name string.
        name = name.replace("PR", "P")

    if "FP-" in name:
        # Replace FP- for FP in name string.
        name = name.replace("FP-", "FP")

    if any(y in name for y in CORRECTIONS):
        # Add a 0 for consistency. (e.g. P3 -> P03)
        return name[:1] + "0" + name[1:]
    return name


def filter_unknown(data: str) -> str | None:
    """Filter unknown values from the data."""
    if data in FILTER_UNKNOWN:
        return None
    return data
