# pylint: disable=W0621
"""Asynchronous Python client providing Open Data information of Amsterdam."""

import asyncio

from odp_amsterdam import Garage, ODPAmsterdam


async def main() -> None:
    """Show example on using the Garage Amsterdam API client."""
    async with ODPAmsterdam() as client:
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
