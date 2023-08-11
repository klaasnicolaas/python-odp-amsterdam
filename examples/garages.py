# pylint: disable=W0621
"""Asynchronous Python client providing Open Data information of Amsterdam."""
from __future__ import annotations

import asyncio

from odp_amsterdam import Garage, ODPAmsterdam


async def main() -> None:
    """Show example on using the ODP Amsterdam API client."""
    async with ODPAmsterdam() as client:
        garages = await client.all_garages(vehicle="car", category="garage")
        single_garage: Garage = await client.garage(
            garage_id="99b77fc5-a237-4ba0-abe4-b9a3886aa471",
        )

        print(f"Single garage: {single_garage}")
        print()

        count: int = len(garages)
        for item in garages:
            print(item)

        # Count unique id's in disabled_parkings
        unique_values: list[str] = [str(item.garage_id) for item in garages]
        num_values = len(set(unique_values))

        print("__________________________")
        print(f"Total garages found: {count}")
        print(f"Unique ID values: {num_values}")


if __name__ == "__main__":
    asyncio.run(main())
