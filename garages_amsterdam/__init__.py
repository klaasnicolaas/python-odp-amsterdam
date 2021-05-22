"""Fetch latest parking garage information from Amsterdam."""
from aiohttp import ClientSession, ClientResponseError
from dataclasses import dataclass
import logging

@dataclass
class AmsterdamCase:
    """Class for garages Amsterdam"""

    URL = "http://opd.it-t.nl/data/amsterdam/ParkingLocation.json"
    NAME = "Garages Amsterdam"

    id: str
    garage_name: str
    state: str
    free_space_short: int
    free_space_long: int
    short_capacity: int
    long_capacity: int
    longitude: float
    latitude: float

    @staticmethod
    def from_json(item):
        attrs = item["properties"]
        point = item["geometry"]["coordinates"]
        id = item
        return AmsterdamCase(
            id=id["Id"],
            garage_name=correct_name(attrs["Name"]),
            state=attrs["State"],
            free_space_short=attrs["FreeSpaceShort"],
            free_space_long=attrs["FreeSpaceLong"],
            short_capacity=attrs["ShortCapacity"],
            long_capacity=attrs["LongCapacity"],
            longitude=split_coordinates("lon", str(point)),
            latitude=split_coordinates("lat", str(point)),
        )

DEFAULT_SOURCE = AmsterdamCase

def split_coordinates(type, data):
    """Split the coordinate data in separate variables."""
    longitude,latitude = data.split(', ')
    longitude = longitude.replace('[', '')
    latitude = latitude.replace(']', '')
    if type == "lon":
        return longitude
    elif type == "lat":
        return latitude

def correct_name(name):
    """Change parking garage name for consistency if needed."""
    filter = ["CE-","ZD-","ZO-","ZU-","FJ212P34 ","VRN-FJ212"]
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
    resp = await session.get(source.URL)
    data = await resp.json(content_type=None)

    if 'error' in data:
        raise ClientResponseError(
            resp.request_info,
            resp.history,
            status=data['error']['code'],
            message=data['error']['message'],
            headers=resp.headers
        )

    results = []
    wrongKeys = ['FP','Fiets']

    for item in data["features"]:
        try:
            if not any(x in item["properties"]["Name"] for x in wrongKeys):
                results.append(source.from_json(item))
        except KeyError:
            logging.getLogger(__name__).warning("Got wrong data: %s", item)

    return results