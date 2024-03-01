"""Test the models."""

from __future__ import annotations

import pytest
from aiohttp import ClientSession
from aresponses import ResponsesMockServer

from odp_amsterdam import (
    Garage,
    ODPAmsterdam,
    ODPAmsterdamError,
    ODPAmsterdamResultsError,
    ParkingSpot,
)

from . import load_fixtures


async def test_all_garages(aresponses: ResponsesMockServer) -> None:
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
    async with ClientSession() as session:
        client = ODPAmsterdam(session=session)
        garages: list[Garage] = await client.all_garages()
        assert garages is not None


async def test_single_garage(aresponses: ResponsesMockServer) -> None:
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
    async with ClientSession() as session:
        client = ODPAmsterdam(session=session)
        garage: Garage = await client.garage("A557D1AD-5D39-915B-8B54-A4AAFA2C1CFC")
        assert garage.garage_name == "P02 Olympisch Stadion"
        assert garage.vehicle == "car"
        assert garage.category == "garage"
        assert garage.state == "ok"
        assert garage.free_space_long == 98
        assert garage.long_capacity == 250
        assert garage.free_space_short == 245
        assert garage.short_capacity == 400
        assert garage.availability_pct == 61.3


async def test_filter_garage_model(aresponses: ResponsesMockServer) -> None:
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
    async with ClientSession() as session:
        client = ODPAmsterdam(session=session)
        garages: list[Garage] = await client.all_garages(
            vehicle="car",
            category="park_and_ride",
        )
        assert garages is not None


async def test_parking_locations_model(aresponses: ResponsesMockServer) -> None:
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
    async with ClientSession() as session:
        client = ODPAmsterdam(session=session)
        locations: list[ParkingSpot] = await client.locations()
        assert locations is not None
        for item in locations:
            assert isinstance(item, ParkingSpot)
            assert item.spot_id is not None
            assert isinstance(item.spot_id, str)
            assert isinstance(item.spot_type, str)
            assert isinstance(item.street, str) or item.street is None
            assert item.coordinates is not None
            assert isinstance(item.coordinates, list)


async def test_wrong_garage_model(aresponses: ResponsesMockServer) -> None:
    """Test a wrong garage model."""
    aresponses.add(
        "api.data.amsterdam.nl",
        "/dcatd/datasets/9ORkef6T-aU29g/purls/1",
        "GET",
        aresponses.Response(
            status=200,
            headers={"Content-Type": "text/plain"},
            text=load_fixtures("wrong_garages.json"),
        ),
    )
    async with ClientSession() as session:
        client = ODPAmsterdam(session=session)
        with pytest.raises(ODPAmsterdamError):
            await client.all_garages()


async def test_no_garage_found(aresponses: ResponsesMockServer) -> None:
    """Test a wrong garage model."""
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
    async with ClientSession() as session:
        client = ODPAmsterdam(session=session)
        with pytest.raises(ODPAmsterdamResultsError):
            await client.garage(garage_id="test")
