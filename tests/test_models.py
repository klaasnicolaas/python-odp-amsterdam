"""Test the models."""

from __future__ import annotations

import json
from typing import TYPE_CHECKING

from aresponses import ResponsesMockServer
from syrupy.assertion import SnapshotAssertion

from odp_amsterdam import ParkingSpot

from . import load_fixtures

if TYPE_CHECKING:
    from odp_amsterdam import Garage, ODPAmsterdam


async def test_all_garages(
    aresponses: ResponsesMockServer,
    snapshot: SnapshotAssertion,
    odp_amsterdam_client: ODPAmsterdam,
) -> None:
    """Test all garage function."""
    aresponses.add(
        "p-info.vorin-amsterdam.nl",
        "/v1/ParkingLocation.json",
        "GET",
        aresponses.Response(
            status=200,
            headers={"Content-Type": "text/plain"},
            text=load_fixtures("garages.json"),
        ),
    )
    garages: list[Garage] = await odp_amsterdam_client.all_garages()
    assert garages == snapshot


async def test_single_garage(
    aresponses: ResponsesMockServer,
    snapshot: SnapshotAssertion,
    odp_amsterdam_client: ODPAmsterdam,
) -> None:
    """Test a single garage model."""
    aresponses.add(
        "p-info.vorin-amsterdam.nl",
        "/v1/ParkingLocation.json",
        "GET",
        aresponses.Response(
            status=200,
            headers={"Content-Type": "text/plain"},
            text=load_fixtures("garages.json"),
        ),
    )
    garage: Garage = await odp_amsterdam_client.garage(
        "A557D1AD-5D39-915B-8B54-A4AAFA2C1CFC"
    )
    assert garage == snapshot


async def test_filter_garage_model(
    aresponses: ResponsesMockServer,
    snapshot: SnapshotAssertion,
    odp_amsterdam_client: ODPAmsterdam,
) -> None:
    """Test on filtering the garage data."""
    aresponses.add(
        "p-info.vorin-amsterdam.nl",
        "/v1/ParkingLocation.json",
        "GET",
        aresponses.Response(
            status=200,
            headers={"Content-Type": "text/plain"},
            text=load_fixtures("garages.json"),
        ),
    )
    garages: list[Garage] = await odp_amsterdam_client.all_garages(
        vehicle="car",
        category="park_and_ride",
    )
    assert garages == snapshot


def test_parking_locations_model() -> None:
    """Preserve the source fields from the existing parking fixture."""
    source = json.loads(load_fixtures("parking.json"))["features"][0]
    record = ParkingSpot.from_json(source)
    assert record.spot_id == source["properties"]["id"]
    assert record.geometry == source["geometry"]
    assert record.coordinates == source["geometry"]["coordinates"][0]
    assert record.regimes == source["properties"]["regimes"]
    assert record.number == source["properties"]["aantal"]
