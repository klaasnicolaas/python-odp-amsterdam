"""Models for Garages Amsterdam."""
from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any

from .const import CORRECTIONS, FILTER, WRONGKEYS
from .exceptions import GaragesAmsterdamError


@dataclass
class Garages:
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

    @staticmethod
    def from_json(data: dict[str, Any]) -> Garages:
        """Return Garages object from the Garages Amsterdam API.

        Args:
            data: The JSON data from the API.

        Returns:
            An Garages object.

        Raises:
            GaragesAmsterdamError: If the data is not valid.
        """

        data = json.loads(data)
        results = []

        for item in data["features"]:
            try:
                if not any(x in item["properties"]["Name"] for x in WRONGKEYS):
                    latitude, longitude = split_coordinates(
                        str(item["geometry"]["coordinates"])
                    )
                    results.append(
                        Garages(
                            garage_id=item["Id"],
                            garage_name=correct_name(item["properties"]["Name"]),
                            state=item["properties"]["State"],
                            free_space_short=item["properties"]["FreeSpaceShort"],
                            free_space_long=item["properties"]["FreeSpaceLong"],
                            short_capacity=item["properties"]["ShortCapacity"],
                            long_capacity=item["properties"]["LongCapacity"],
                            longitude=longitude,
                            latitude=latitude,
                        )
                    )
            except KeyError as exception:
                raise GaragesAmsterdamError(f"Got wrong data: {item}") from exception
        return results


def split_coordinates(data):
    """Split the coordinate data in separate variables.

    Args:
        data: The data to be split.

    Returns:
        The coordinates.
    """

    longitude, latitude = data.split(", ")
    longitude = longitude.replace("[", "")
    latitude = latitude.replace("]", "")
    return latitude, longitude


def correct_name(name):
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
