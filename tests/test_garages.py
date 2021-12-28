"""Basic tests for the Garages Amsterdam API."""
# pylint: disable=protected-access
from unittest.mock import patch

import aiohttp
import pytest

from garages_amsterdam import GaragesAmsterdam
from garages_amsterdam.exceptions import GaragesAmsterdamConnectionError


@pytest.mark.asyncio
async def test_client_error():
    """Test request client error from the Garages Amsterdam API."""
    async with aiohttp.ClientSession() as session:
        client = GaragesAmsterdam(session=session)
        with patch.object(
            session, "request", side_effect=aiohttp.ClientError
        ), pytest.raises(GaragesAmsterdamConnectionError):
            assert await client._request("test")
