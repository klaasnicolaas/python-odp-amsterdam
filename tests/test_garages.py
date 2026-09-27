"""Test the garages on exceptions."""

from __future__ import annotations

import json

import pytest
from aresponses import ResponsesMockServer

from odp_amsterdam import ODPAmsterdam, ODPAmsterdamError, ODPAmsterdamResultsError

from . import load_fixtures


@pytest.mark.parametrize("vehicle", ["car", "bicycle", "touringcar"])
async def test_vehicle_filter_with_current_source_names(
    vehicle: str,
    aresponses: ResponsesMockServer,
    odp_amsterdam_client: ODPAmsterdam,
) -> None:
    """Filter current feed names through the public client API."""
    features = []
    for source_id, name in (
        ("car", "P-106_ Byzantium (opendata)"),
        ("bicycle", "FP-012_ Leidseplein "),
        ("touringcar", "PT-001_ Touringcar"),
    ):
        feature = json.loads(load_fixtures("garages.json"))["features"][0]
        feature["Id"] = source_id
        feature["properties"]["Name"] = name
        feature["geometry"]["coordinates"] = [52.362386365926604, 4.883357405662521]
        features.append(feature)
    aresponses.add(
        "p-info.vorin-amsterdam.nl",
        "/v1/ParkingLocation.json",
        "GET",
        aresponses.Response(
            status=200,
            headers={"Content-Type": "application/json"},
            text=json.dumps({"features": features}),
        ),
    )
    garages = await odp_amsterdam_client.all_garages(vehicle=vehicle)
    assert [garage.garage_id for garage in garages] == [vehicle]
    assert garages[0].vehicle == vehicle
    assert garages[0].latitude == 52.362386365926604
    assert garages[0].longitude == 4.883357405662521


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
