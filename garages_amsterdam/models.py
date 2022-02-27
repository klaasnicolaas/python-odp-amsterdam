"""Models for Garages Amsterdam."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .const import CORRECTIONS, FILTER


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
    longitude: float
    latitude: float

    @classmethod
    def from_json(cls, data: dict[str, Any]) -> Garage:
        """Return Garages object from the Garages Amsterdam API.

        Args:
            data: The JSON data from the API.

        Returns:
            An Garages object.
        """
        latitude, longitude = split_coordinates(str(data["geometry"]["coordinates"]))

        return cls(
            garage_id=data["Id"],
            garage_name=correct_name(data["properties"]["Name"]),
            state=data["properties"]["State"],
            free_space_short=data["properties"]["FreeSpaceShort"],
            free_space_long=data["properties"]["FreeSpaceLong"],
            short_capacity=data["properties"]["ShortCapacity"],
            long_capacity=data["properties"]["LongCapacity"],
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


def correct_name(name: str) -> str:
    """Change parking garage name for consistency if needed.

    Args:
        name: The name of the parking garage.

    Returns:
        The corrected name.
    """

    for value in FILTER:
        # Remove parts from name string.
        name = name.replace(value, "")

    if any(y in name for y in CORRECTIONS):
        # Add a 0 for consistency.
        return name[:1] + "0" + name[1:]
    return name
