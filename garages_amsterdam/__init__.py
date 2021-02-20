"""Fetch latest parking garage information from Amsterdam."""
from aiohttp import ClientSession
from dataclasses import dataclass
from .import errors

import logging
import aiohttp
import asyncio

_LOGGER = logging.getLogger(__name__)

@dataclass
class AmsterdamCase:
    """Class for garages Amsterdam"""

    URL = "http://opd.it-t.com/data/amsterdam/ParkingLocation.json"
    NAME = "Garages Amsterdam"

    id: str
    garage_name: str
    state: str
    free_space_short: int
    free_space_long: int
    short_capacity: int
    long_capacity: int

    @staticmethod
    def from_json(item):
        attrs = item["properties"]
        id = item
        return AmsterdamCase(
            id=id["Id"],
            garage_name=correct_name(attrs["Name"]),
            state=attrs["State"],
            free_space_short=attrs["FreeSpaceShort"],
            free_space_long=attrs["FreeSpaceLong"],
            short_capacity=attrs["ShortCapacity"],
            long_capacity=attrs["LongCapacity"],
        )

DEFAULT_SOURCE = AmsterdamCase

def correct_name(name):
    """Change parking garage name for consistency if needed."""
    filter = ["CE-","ZD-","ZO-","ZU-","FJ212P34 "]
    corrections = ["P1 ", "P3 "]
    
    for value in filter:
        """Remove parts from name string."""
        name = name.replace(value, '')

    if any(y in name for y in corrections):
        """Add a 0 for consistency."""
        return name[:1] + '0' + name[1:]
    else:
        return name

async def get_garages(session: ClientSession, *, source=DEFAULT_SOURCE):
    """Fetch parking garage data."""
    try:
        resp = await session.get(source.URL)
    except aiohttp.ClientConnectionError as err:
        _LOGGER.debug("Failed to connect")
        errors.raise_error(err, 1)
    except aiohttp.InvalidURL as err:
        _LOGGER.debug("Could not connect, API url is incorrect")
        errors.raise_error(err, 1)
    except aiohttp.ClientResponseError as err:
        _LOGGER.debug("Caught response error: %s", err)
        errors.raise_error(err, 2)
    except (aiohttp.ClientError, asyncio.TimeoutError) as err:
        _LOGGER.debug("Unknown error occurred")
        errors.raise_error(err, 3)

    data = await resp.json(content_type=None)

    results = []
    wrongKeys = ['FP','Fiets']

    for item in data["features"]:
        try:
            if not any(x in item["properties"]["Name"] for x in wrongKeys):
                results.append(source.from_json(item))
        except KeyError:
            logging.getLogger(__name__).warning("Got wrong data: %s", item)
    return results