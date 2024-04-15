"""Test the models."""

from __future__ import annotations

from typing import TYPE_CHECKING

from aresponses import ResponsesMockServer
from syrupy.assertion import SnapshotAssertion

from . import load_fixtures

if TYPE_CHECKING:
    from odp_amsterdam import Garage, ODPAmsterdam, ParkingSpot


async def test_all_garages(
    aresponses: ResponsesMockServer,
    snapshot: SnapshotAssertion,
    odp_amsterdam_client: ODPAmsterdam,
) -> None:
    """Test all garage function."""
    aresponses.add(
        "api.data.amsterdam.nl",
        "/dcatd/datasets/9ORkef6T-aU29g/purls/1",
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
        "api.data.amsterdam.nl",
        "/dcatd/datasets/9ORkef6T-aU29g/purls/1",
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
        "api.data.amsterdam.nl",
        "/dcatd/datasets/9ORkef6T-aU29g/purls/1",
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


async def test_parking_locations_model(
    aresponses: ResponsesMockServer,
    snapshot: SnapshotAssertion,
    odp_amsterdam_client: ODPAmsterdam,
) -> None:
    """Test the parking locations model."""
    aresponses.add(
        "api.data.amsterdam.nl",
        "/v1/parkeervakken/parkeervakken",
        "GET",
        aresponses.Response(
            status=200,
            headers={"Content-Type": "application/geo+json"},
            text=load_fixtures("parking.json"),
        ),
    )
    locations: list[ParkingSpot] = await odp_amsterdam_client.locations()
    assert locations == snapshot
