"""Asynchronous Python client providing Open Data information of Amsterdam."""

from __future__ import annotations

import asyncio

from odp_amsterdam import ODPAmsterdam


async def main() -> None:
    """Show example on using the ODP Amsterdam API client."""
    async with ODPAmsterdam() as client:
        locations = await client.locations(
            limit=10,
            parking_type="E6a",
        )

        count: int = len(locations.records)
        for item in locations.records:
            print(item)

        # Count unique id's in disabled_parkings
        unique_values: list[str] = [str(item.spot_id) for item in locations.records]
        num_values = len(set(unique_values))

        print("__________________________")
        print(f"Locations found: {count} / {locations.total_count}")
        print(f"Complete selection: {locations.complete}")
        print(f"Unique ID values: {num_values}")


if __name__ == "__main__":
    asyncio.run(main())
