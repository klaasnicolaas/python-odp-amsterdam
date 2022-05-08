"""Test the models."""
import aiohttp
import pytest
from aresponses import ResponsesMockServer

from garages_amsterdam import (
    Garage,
    GaragesAmsterdam,
    GaragesAmsterdamError,
    GaragesAmsterdamResultsError,
)

from . import load_fixtures


@pytest.mark.asyncio
async def test_all_garages(aresponses: ResponsesMockServer) -> None:
    """Test all garage function."""
    aresponses.add(
        "opd.it-t.nl",
        "/data/amsterdam/ParkingLocation.json",
        "GET",
        aresponses.Response(
            status=200,
            headers={"Content-Type": "text/plain"},
            text=load_fixtures("garages.txt"),
        ),
    )
    async with aiohttp.ClientSession() as session:
        client = GaragesAmsterdam(session=session)
        garages: list[Garage] = await client.all_garages()
        assert garages is not None


@pytest.mark.asyncio
async def test_single_garage(aresponses: ResponsesMockServer) -> None:
    """Test a single garage model."""
    aresponses.add(
        "opd.it-t.nl",
        "/data/amsterdam/ParkingLocation.json",
        "GET",
        aresponses.Response(
            status=200,
            headers={"Content-Type": "text/plain"},
            text=load_fixtures("garages.txt"),
        ),
    )
    async with aiohttp.ClientSession() as session:
        client = GaragesAmsterdam(session=session)
        garage: Garage = await client.garage("900000001_parkinglocation")
        assert garage.garage_name == "P02 P Olympisch stadion"
        assert garage.free_space_long == "228"
        assert garage.free_space_short == "273"


@pytest.mark.asyncio
async def test_wrong_garage_model(aresponses: ResponsesMockServer) -> None:
    """Test a wrong garage model."""
    aresponses.add(
        "opd.it-t.nl",
        "/data/amsterdam/ParkingLocation.json",
        "GET",
        aresponses.Response(
            status=200,
            headers={"Content-Type": "text/plain"},
            text=load_fixtures("wrong_garages.txt"),
        ),
    )
    async with aiohttp.ClientSession() as session:
        client = GaragesAmsterdam(session=session)
        with pytest.raises(GaragesAmsterdamError):
            garages: list[Garage] = await client.all_garages()
            assert garages is not None


@pytest.mark.asyncio
async def test_no_garage_found(aresponses: ResponsesMockServer) -> None:
    """Test a wrong garage model."""
    aresponses.add(
        "opd.it-t.nl",
        "/data/amsterdam/ParkingLocation.json",
        "GET",
        aresponses.Response(
            status=200,
            headers={"Content-Type": "text/plain"},
            text=load_fixtures("garages.txt"),
        ),
    )
    async with aiohttp.ClientSession() as session:
        client = GaragesAmsterdam(session=session)
        with pytest.raises(GaragesAmsterdamResultsError):
            garage = await client.garage(garage_id="test")
            assert garage is None
