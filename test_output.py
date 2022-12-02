# pylint: disable=W0621
"""Asynchronous Python client providing Open Data information of Amsterdam."""

import asyncio

from odp_amsterdam import Garage, ODPAmsterdam


async def main() -> None:
    """Show example on using the ODP Amsterdam API client."""
    async with ODPAmsterdam() as client:
        count: int

        garages: list[Garage] = await client.all_garages()
        locations = await client.locations(limit=10, parking_type="E6a")
        garage = await client.garage(garage_id="900000001_parkinglocation")

        print(garages)
        print()
        print(garage)
        print()

        for index, item in enumerate(locations, 1):
            count = index
            print(item)

        # # Count unique id's in disabled_parkings
        unique_values: list[str] = []
        for location in locations:
            unique_values.append(location.spot_id)
        num_values = len(set(unique_values))

        print("__________________________")
        print(f"Total locations found: {count}")
        print(f"Unique ID values: {num_values}")


if __name__ == "__main__":
    asyncio.run(main())
