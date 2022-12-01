"""Test the models."""
import aiohttp
import pytest
from aresponses import ResponsesMockServer

from odp_amsterdam import (
    Garage,
    ODPAmsterdam,
    ODPAmsterdamError,
    ODPAmsterdamResultsError,
)

from . import load_fixtures


@pytest.mark.asyncio
async def test_all_garages(aresponses: ResponsesMockServer) -> None:
    """Test all garage function."""
    aresponses.add(
        "api.data.amsterdam.nl",
        "/dcatd/datasets/9ORkef6T-aU29g/purls/l6HdY0TFamuFOQ",
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
        "/dcatd/datasets/9ORkef6T-aU29g/purls/l6HdY0TFamuFOQ",
        "GET",
        aresponses.Response(
            status=200,
            headers={"Content-Type": "text/plain"},
            text=load_fixtures("garages.json"),
        ),
    )
    async with aiohttp.ClientSession() as session:
        client = ODPAmsterdam(session=session)
        garage: Garage = await client.garage("900000001_parkinglocation")
        assert garage.garage_name == "P02 P Olympisch stadion"
        assert garage.free_space_long == "228"
        assert garage.free_space_short == "273"
        assert garage.availability_pct == 88.3


@pytest.mark.asyncio
async def test_wrong_garage_model(aresponses: ResponsesMockServer) -> None:
    """Test a wrong garage model."""
    aresponses.add(
        "api.data.amsterdam.nl",
        "/dcatd/datasets/9ORkef6T-aU29g/purls/l6HdY0TFamuFOQ",
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
        "/dcatd/datasets/9ORkef6T-aU29g/purls/l6HdY0TFamuFOQ",
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
