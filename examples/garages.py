# pylint: disable=W0621
"""Asynchronous Python client providing Open Data information of Amsterdam."""

import asyncio

from odp_amsterdam import Garage, ODPAmsterdam


async def main() -> None:
    """Show example on using the ODP Amsterdam API client."""
    async with ODPAmsterdam() as client:
        count: int

        garages = await client.all_garages()
        garage: Garage = await client.garage(
            garage_id="99b77fc5-a237-4ba0-abe4-b9a3886aa471",
        )

        print(garage)
        print()

        for index, item in enumerate(garages, 1):
            count = index
            print(item)

        # # Count unique id's in disabled_parkings
        unique_values: list[str] = []
        for location in garages:
            unique_values.append(location.garage_id)
        num_values = len(set(unique_values))

        print("__________________________")
        print(f"Total garages found: {count}")
        print(f"Unique ID values: {num_values}")


if __name__ == "__main__":
    asyncio.run(main())
