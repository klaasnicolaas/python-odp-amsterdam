"""Test the garages on exceptions."""

from __future__ import annotations

import pytest
from aresponses import ResponsesMockServer

from odp_amsterdam import ODPAmsterdam, ODPAmsterdamError, ODPAmsterdamResultsError

from . import load_fixtures


async def test_wrong_garage_model(
    aresponses: ResponsesMockServer,
    odp_amsterdam_client: ODPAmsterdam,
) -> None:
    """Test a wrong garage model."""
    aresponses.add(
        "p-info.vorin-amsterdam.nl",
        "/v1/ParkingLocation.json",
        "GET",
        aresponses.Response(
            status=200,
            headers={"Content-Type": "text/plain"},
            text=load_fixtures("wrong_garages.json"),
        ),
    )
    with pytest.raises(ODPAmsterdamError):
        await odp_amsterdam_client.all_garages()


async def test_no_garage_found(
    aresponses: ResponsesMockServer,
    odp_amsterdam_client: ODPAmsterdam,
) -> None:
    """Test a wrong garage model."""
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
    with pytest.raises(ODPAmsterdamResultsError):
        await odp_amsterdam_client.garage(garage_id="test")
