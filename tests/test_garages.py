"""Basic tests for the Garages Amsterdam API."""
# pylint: disable=protected-access
import asyncio
from unittest.mock import patch

import aiohttp
import pytest

from garages_amsterdam import GaragesAmsterdam
from garages_amsterdam.exceptions import (
    GaragesAmsterdamConnectionError,
    GaragesAmsterdamError,
)

from . import load_fixtures


@pytest.mark.asyncio
async def test_json_request(aresponses):
    """Test JSON response is handled correctly."""
    aresponses.add(
        "opd.it-t.nl",
        "/data/amsterdam/test",
        "GET",
        aresponses.Response(
            status=200,
            headers={"Content-Type": "text/plain"},
            text=load_fixtures("garages.txt"),
        ),
    )
    async with aiohttp.ClientSession() as session:
        client = GaragesAmsterdam(session=session)
        response = await client._request("test")
        assert response is not None
        await client.close()


@pytest.mark.asyncio
async def test_internal_session(aresponses):
    """Test internal session is handled correctly."""
    aresponses.add(
        "opd.it-t.nl",
        "/data/amsterdam/test",
        "GET",
        aresponses.Response(
            status=200,
            headers={"Content-Type": "text/plain"},
            text=load_fixtures("garages.txt"),
        ),
    )
    async with GaragesAmsterdam() as client:
        await client._request("test")


@pytest.mark.asyncio
async def test_timeout(aresponses):
    """Test request timeout from the Garages Amsterdam API."""
    # Faking a timeout by sleeping
    async def response_handler(_):
        await asyncio.sleep(0.2)
        return aresponses.Response(
            body="Goodmorning!", text=load_fixtures("garages.txt")
        )

    aresponses.add("opd.it-t.nl", "/data/amsterdam/test", "GET", response_handler)

    async with aiohttp.ClientSession() as session:
        client = GaragesAmsterdam(
            session=session,
            request_timeout=0.1,
        )
        with pytest.raises(GaragesAmsterdamConnectionError):
            assert await client._request("test")


@pytest.mark.asyncio
async def test_content_type(aresponses):
    """Test request content type error from Garages Amsterdam API."""
    aresponses.add(
        "opd.it-t.nl",
        "/data/amsterdam/test",
        "GET",
        aresponses.Response(
            status=200,
            headers={"Content-Type": "blabla/blabla"},
        ),
    )

    async with aiohttp.ClientSession() as session:
        client = GaragesAmsterdam(session=session)
        with pytest.raises(GaragesAmsterdamError):
            assert await client._request("test")


@pytest.mark.asyncio
async def test_client_error():
    """Test request client error from the Garages Amsterdam API."""
    async with aiohttp.ClientSession() as session:
        client = GaragesAmsterdam(session=session)
        with patch.object(
            session, "request", side_effect=aiohttp.ClientError
        ), pytest.raises(GaragesAmsterdamConnectionError):
            assert await client._request("test")
