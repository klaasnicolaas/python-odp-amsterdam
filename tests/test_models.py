"""Test the models."""

from __future__ import annotations

import json
from typing import TYPE_CHECKING

import pytest
from aresponses import ResponsesMockServer
from syrupy.assertion import SnapshotAssertion

from odp_amsterdam import ParkingSpot
from odp_amsterdam.models import Garage, GarageCategory, VehicleType

from . import load_fixtures

if TYPE_CHECKING:
    from odp_amsterdam import ODPAmsterdam


async def test_all_garages(
    aresponses: ResponsesMockServer,
    snapshot: SnapshotAssertion,
    odp_amsterdam_client: ODPAmsterdam,
) -> None:
    """Test all garage function."""
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
    garages: list[Garage] = await odp_amsterdam_client.all_garages()
    assert garages == snapshot


async def test_single_garage(
    aresponses: ResponsesMockServer,
    snapshot: SnapshotAssertion,
    odp_amsterdam_client: ODPAmsterdam,
) -> None:
    """Test a single garage model."""
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
    garage: Garage = await odp_amsterdam_client.garage(
        "A557D1AD-5D39-915B-8B54-A4AAFA2C1CFC"
    )
    assert garage == snapshot


async def test_filter_garage_model(
    aresponses: ResponsesMockServer,
    snapshot: SnapshotAssertion,
    odp_amsterdam_client: ODPAmsterdam,
) -> None:
    """Test on filtering the garage data."""
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
    garages: list[Garage] = await odp_amsterdam_client.all_garages(
        vehicle="car",
        category="park_and_ride",
    )
    assert garages == snapshot


def test_parking_locations_model() -> None:
    """Preserve the source fields from the existing parking fixture."""
    source = json.loads(load_fixtures("parking.json"))["features"][0]
    record = ParkingSpot.from_json(source)
    assert record.spot_id == source["properties"]["id"]
    assert record.geometry == source["geometry"]
    assert record.coordinates == source["geometry"]["coordinates"][0]
    assert record.regimes == source["properties"]["regimes"]
    assert record.number == source["properties"]["aantal"]


@pytest.mark.parametrize(
    "coordinates",
    [[52.362386365926604, 4.883357405662521], [4.883357405662521, 52.362386365926604]],
)
@pytest.mark.parametrize("name", ["FP-012_ Leidseplein ", "CE-FP09 De Munt"])
def test_current_and_legacy_garage_source_mapping(
    coordinates: list[float],
    name: str,
) -> None:
    """Handle the current provider axis order and bicycle prefixes."""
    source = json.loads(load_fixtures("garages.json"))["features"][0]
    source["geometry"]["coordinates"] = coordinates
    source["properties"]["Name"] = name
    garage = Garage.from_json(source)
    assert garage.latitude == 52.362386365926604
    assert garage.longitude == 4.883357405662521
    assert garage.vehicle == VehicleType.BICYCLE


@pytest.mark.parametrize(
    "coordinates", [[0, 0], [52.3], [True, 4.9], [52.3, float("nan")]]
)
def test_invalid_garage_coordinates_are_not_guessed(coordinates: list[float]) -> None:
    """Fail on malformed or geographically ambiguous provider coordinates."""
    source = json.loads(load_fixtures("garages.json"))["features"][0]
    source["geometry"]["coordinates"] = coordinates
    with pytest.raises(ValueError, match="coordinates"):
        Garage.from_json(source)


@pytest.mark.parametrize(
    ("source_name", "name", "category"),
    [
        ("P-106_ Byzantium (opendata)", "Byzantium", GarageCategory.GARAGE),
        (
            "P-223_ Amsterdamse Poort P23 (opendata)",
            "Amsterdamse Poort P23",
            GarageCategory.GARAGE,
        ),
        ("P-204_ P4 Villa Arena", "P4 Villa Arena", GarageCategory.GARAGE),
        ("P-201_ P1 ArenA", "P1 ArenA", GarageCategory.GARAGE),
        ("PR-004_ Zeeburg 2", "P+R Zeeburg 2", GarageCategory.PARK_AND_RIDE),
        (
            "PR-002_ Olympisch Stadion P+R",
            "Olympisch Stadion P+R",
            GarageCategory.PARK_AND_RIDE,
        ),
        ("P-302_ VUmc (ACTA)", "VUmc (ACTA)", GarageCategory.GARAGE),
        ("CE-P30 Heinekenplein", "P30 Heinekenplein", GarageCategory.GARAGE),
        (
            "  PR-008_  Bos en Lommer (opendata)  ",
            "P+R Bos en Lommer",
            GarageCategory.PARK_AND_RIDE,
        ),
    ],
)
def test_readable_garage_names_keep_meaningful_identifiers(
    source_name: str,
    name: str,
    category: GarageCategory,
) -> None:
    """Remove transport labels while retaining facility numbers and provenance."""
    source = json.loads(load_fixtures("garages.json"))["features"][0]
    source["properties"]["Name"] = source_name
    garage = Garage.from_json(source)
    assert garage.garage_name == name
    assert garage.category == category
    assert garage.source_name == source_name
    assert garage.garage_id == source["Id"]
