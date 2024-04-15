"""Fixtures for the ODP Amsterdam tests."""

from collections.abc import AsyncGenerator

import pytest
from aiohttp import ClientSession

from odp_amsterdam import ODPAmsterdam


@pytest.fixture(name="odp_amsterdam_client")
async def client() -> AsyncGenerator[ODPAmsterdam, None]:
    """ODP Amsterdam client fixture."""
    async with (
        ClientSession() as session,
        ODPAmsterdam(session=session) as odp_amsterdam_client,
    ):
        yield odp_amsterdam_client
