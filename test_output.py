# pylint: disable=W0621
"""Asynchronous Python client for the Garages Amsterdam API."""

import asyncio

from garages_amsterdam import Garage, GaragesAmsterdam


async def main() -> None:
    """Show example on using the Garage Amsterdam API client."""
    async with GaragesAmsterdam() as client:
        garages: list[Garage] = await client.all_garages()
        garage = await client.garage(garage_id="900000001_parkinglocation")
        count: int

        for index, item in enumerate(garages, 1):
            count = index
            print(item)
        print(f"{count} parkeergarages gevonden")
        print("---")
        print(garage)


if __name__ == "__main__":
    asyncio.run(main())
