# pylint: disable=W0621
"""Asynchronous Python client for the Garages Amsterdam API."""

import asyncio

from garages_amsterdam import Garage, GaragesAmsterdam


async def main() -> None:
    """Show example on using the Garage Amsterdam API client."""
    async with GaragesAmsterdam() as client:
        garages: list[Garage] = await client.all_garages()
        count: int

        for index, item in enumerate(garages, 1):
            count = index
            print(item)
        print(f"{count} parkeergarages gevonden")


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
