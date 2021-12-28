"""Test the models."""
import aiohttp
import pytest

from garages_amsterdam import Garage, GaragesAmsterdam, GaragesAmsterdamError

from . import load_fixtures


@pytest.mark.asyncio
async def test_garage_model(aresponses):
    """Test the garage model."""
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
        garages: Garage = await client.all_garages()
        assert garages is not None


@pytest.mark.asyncio
async def test_wrong_garage_model(aresponses):
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
            garages: Garage = await client.all_garages()
            assert garages is not None
