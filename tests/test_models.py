"""Test the models."""
import aiohttp
import pytest
from aresponses import ResponsesMockServer

from odp_amsterdam import (
    Garage,
    ODPAmsterdam,
    ODPAmsterdamError,
    ODPAmsterdamResultsError,
    ParkingSpot,
)

from . import load_fixtures


@pytest.mark.asyncio
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
    async with aiohttp.ClientSession() as session:
        client = ODPAmsterdam(session=session)
        garages: list[Garage] = await client.all_garages()
        assert garages is not None
        for item in garages:
            assert isinstance(item, Garage)
            assert item.garage_id is not None
            assert item.garage_name is not None
            assert item.state is not None


@pytest.mark.asyncio
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
    async with aiohttp.ClientSession() as session:
        client = ODPAmsterdam(session=session)
        garage: Garage = await client.garage("A557D1AD-5D39-915B-8B54-A4AAFA2C1CFC")
        assert garage.garage_name == "P02 Olympisch Stadion"


@pytest.mark.asyncio
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
    async with aiohttp.ClientSession() as session:
        client = ODPAmsterdam(session=session)
        locations: list[ParkingSpot] = await client.locations()
        assert locations is not None
        for item in locations:
            assert isinstance(item, ParkingSpot)
            assert item.spot_id is not None and isinstance(item.spot_id, str)
            assert isinstance(item.spot_type, str)
            assert isinstance(item.street, str) or item.street is None
            assert item.coordinates is not None and isinstance(item.coordinates, list)


@pytest.mark.asyncio
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
    async with aiohttp.ClientSession() as session:
        client = ODPAmsterdam(session=session)
        with pytest.raises(ODPAmsterdamError):
            garages: list[Garage] = await client.all_garages()
            assert garages is not None


@pytest.mark.asyncio
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
    async with aiohttp.ClientSession() as session:
        client = ODPAmsterdam(session=session)
        with pytest.raises(ODPAmsterdamResultsError):
            garage = await client.garage(garage_id="test")
            assert garage is None
