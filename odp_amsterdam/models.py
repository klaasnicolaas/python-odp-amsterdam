"""Models for Open Data Platform of Amsterdam."""
from __future__ import annotations

from dataclasses import dataclass
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
    def from_json(cls, data: dict[str, Any]) -> ParkingSpot:
        """Return ParkingSpot object from a dictionary.

        Args:
            data: The JSON data from the API.

        Returns:
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
            coordinates=data["geometry"]["coordinates"],
        )


@dataclass
class Garage:
    """Object representing an Garage model response from the API."""

    garage_id: str
    garage_name: str
    state: str
    free_space_short: int
    free_space_long: int | None
    short_capacity: int
    long_capacity: int | None
    availability_pct: float | None
    longitude: float
    latitude: float

    @classmethod
    def from_json(cls, data: dict[str, Any]) -> Garage:
        """Return Garage object from a dictionary.

        Args:
            data: The JSON data from the API.

        Returns:
            An Garage object.
        """
        latitude, longitude = split_coordinates(str(data["geometry"]["coordinates"]))
        attr = data["properties"]
        return cls(
            garage_id=data["Id"],
            garage_name=correct_name(data["properties"]["Name"]),
            state=attr.get("State"),
            free_space_short=int(attr["FreeSpaceShort"]),
            free_space_long=None
            if attr["FreeSpaceLong"] == ""
            else int(attr["FreeSpaceLong"]),
            short_capacity=int(attr["ShortCapacity"]),
            long_capacity=None
            if attr["LongCapacity"] == ""
            else int(attr["LongCapacity"]),
            availability_pct=calculate_pct(
                attr.get("FreeSpaceShort"), attr.get("ShortCapacity")
            ),
            longitude=longitude,
            latitude=latitude,
        )


def split_coordinates(data: str) -> tuple[float, float]:
    """Split the coordinate data in separate variables.

    Args:
        data: The data to be split.

    Returns:
        The coordinates.
    """

    longitude, latitude = data.split(", ")
    longitude = longitude.replace("[", "")
    latitude = latitude.replace("]", "")
    return float(latitude), float(longitude)


def calculate_pct(current: int, total: int) -> float | None:
    """Calculate the percentage of free parking spots.

    Args:
        current: The current amount of free parking spots.
        total: The total amount of parking spots.

    Returns:
        The percentage of free parking spots.
    """
    try:
        return round((float(current) / float(total)) * 100, 1)
    except ZeroDivisionError:
        return None


def correct_name(name: str) -> str:
    """Change parking garage name for consistency if needed.

    Args:
        name: The name of the parking garage.

    Returns:
        The corrected name.
    """

    for value in FILTER_NAMES:
        # Remove parts from name string.
        name = name.replace(value, "")

    if any(y in name for y in CORRECTIONS):
        # Add a 0 for consistency. (e.g. P3 -> P03)
        return name[:1] + "0" + name[1:]
    return name


def filter_unknown(data: str) -> str | None:
    """Filter unknown data from the API.

    Args:
        data: The data to be filtered.

    Returns:
        The filtered data.
    """
    if data in FILTER_UNKNOWN:
        return None
    return data
