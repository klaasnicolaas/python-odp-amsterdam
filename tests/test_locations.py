"""Parking retrieval preserves source meaning and verifies pagination."""

from __future__ import annotations

import json
from copy import deepcopy
from datetime import date
from typing import Any
from unittest.mock import AsyncMock, patch

import pytest
from aiohttp.web import Request
from aresponses import Response, ResponsesMockServer

from odp_amsterdam import ODPAmsterdam, ODPAmsterdamError, ParkingSpot

from . import load_fixtures


def feature(identifier: str = "000123") -> dict[str, Any]:
    """Reuse one existing source feature rather than another fixture corpus."""
    data = json.loads(load_fixtures("parking.json"))["features"][0]
    data["properties"]["id"] = identifier
    return data


def page(ids: list[str], total: int, number: int = 1, size: int = 2) -> dict[str, Any]:
    """Build the API's HAL envelope from existing source fields."""
    rows = []
    for identifier in ids:
        data = feature(identifier)
        rows.append({**data["properties"], "geometry": data["geometry"]})
    return {
        "_embedded": {"parkeervakken": rows},
        "page": {"number": number, "size": size, "totalElements": total},
        "_links": {"next": {"href": "unused"}} if number * size < total else {},
    }


async def test_paginated_locations(aresponses: ResponsesMockServer) -> None:
    """Fetch every page and independently recheck the same filtered selection."""
    responses = [page(["001", "002"], 3), page(["003"], 3, 2), page(["001"], 3, size=1)]
    queries = []

    async def handler(request: Request) -> Response:
        assert request.headers["Accept-Crs"] == "EPSG:4326"
        assert request.headers["Accept"] == "application/hal+json"
        assert request.headers["User-Agent"].startswith("PythonODPAmsterdam/")
        queries.append(dict(request.query))
        return Response(
            text=json.dumps(responses.pop(0)), content_type="application/hal+json"
        )

    aresponses.add(
        "api.data.amsterdam.nl",
        "/v1/parkeervakken/parkeervakken",
        "GET",
        handler,
        repeat=3,
    )
    async with ODPAmsterdam() as client:
        result = await client.locations(parking_type="E6a", page_size=2)
    assert [record.spot_id for record in result.records] == ["001", "002", "003"]
    assert (result.total_count, result.pages_fetched, result.complete) == (3, 2, True)
    assert [query["page"] for query in queries] == ["1", "2", "1"]
    assert [query["_pageSize"] for query in queries] == ["2", "2", "1"]
    assert all(
        query["eType"] == "E6a"
        and query["_sort"] == "id"
        and query["_count"] == "true"
        and query["_format"] == "json"
        for query in queries
    )


@pytest.mark.parametrize(("limit", "complete"), [(1, False), (2, True), (3, True)])
async def test_limited_locations(limit: int, *, complete: bool) -> None:
    """Finite limits retain the reported total and accurately report completeness."""
    size = min(2, limit)
    payload = page(["001", "002"][:size], 2, size=size)
    with patch.object(
        ODPAmsterdam,
        "_request",
        new=AsyncMock(side_effect=[payload, page(["001"], 2, size=1)]),
    ):
        result = await ODPAmsterdam().locations(limit=limit, page_size=2)
    assert len(result.records) == min(limit, 2)
    assert result.total_count == 2
    assert result.complete is complete


async def test_limit_crosses_page_boundary() -> None:
    """Trim only the requested result while validating the received pages."""
    with patch.object(
        ODPAmsterdam,
        "_request",
        new=AsyncMock(
            side_effect=[
                page(["1", "2"], 4),
                page(["3", "4"], 4, 2),
                page(["1"], 4, size=1),
            ]
        ),
    ):
        result = await ODPAmsterdam().locations(limit=3, page_size=2)
    assert [record.spot_id for record in result.records] == ["1", "2", "3"]
    assert not result.complete


async def test_empty_selection() -> None:
    """An explicitly empty source selection is distinct from missing metadata."""
    with patch.object(
        ODPAmsterdam,
        "_request",
        new=AsyncMock(side_effect=[page([], 0), page([], 0, size=1)]),
    ):
        result = await ODPAmsterdam().locations(page_size=2)
    assert result.records == []
    assert result.total_count == 0
    assert result.complete


@pytest.mark.parametrize(
    "failure",
    [
        "duplicate",
        "changed_total",
        "short_page",
        "next_missing",
        "metadata_missing",
        "record_missing",
        "end_total",
        "end_version",
        "end_id",
    ],
)
async def test_incomplete_retrieval_fails(failure: str) -> None:
    """Never return a partial success after inconsistent source responses."""
    responses = [page(["001", "002"], 3), page(["003"], 3, 2), page(["001"], 3, size=1)]
    if failure == "duplicate":
        responses[1] = page(["001"], 3, 2)
    elif failure == "changed_total":
        responses[1] = page(["003", "004"], 4, 2)
    elif failure == "short_page":
        responses[1]["_embedded"]["parkeervakken"] = []
    elif failure == "next_missing":
        responses[0]["_links"] = {}
    elif failure == "metadata_missing":
        del responses[0]["page"]["totalElements"]
    elif failure == "record_missing":
        del responses[1]["_embedded"]["parkeervakken"][0]["regimes"]
    elif failure == "end_total":
        responses[2] = page(["001"], 4, size=1)
    elif failure == "end_version":
        responses[2]["_embedded"]["parkeervakken"][0]["versiedatum"] = "2030-01-01"
    else:
        responses[2]["_embedded"]["parkeervakken"][0]["id"] = "different"
    with (
        patch.object(ODPAmsterdam, "_request", new=AsyncMock(side_effect=responses)),
        pytest.raises(ODPAmsterdamError),
    ):
        await ODPAmsterdam().locations(page_size=2)


async def test_failure_after_first_page() -> None:
    """An upstream error after a successful page propagates without a result."""
    with (
        patch.object(
            ODPAmsterdam,
            "_request",
            new=AsyncMock(
                side_effect=[
                    page(["001", "002"], 3),
                    ODPAmsterdamError("source failed"),
                ]
            ),
        ),
        pytest.raises(ODPAmsterdamError, match="source failed"),
    ):
        await ODPAmsterdam().locations(page_size=2)


@pytest.mark.parametrize(
    "options",
    [
        {"limit": 0},
        {"limit": -1},
        {"limit": True},
        {"page_size": 0},
        {"page_size": 1001},
    ],
)
async def test_invalid_bounds(options: dict[str, Any]) -> None:
    """Invalid request bounds fail before contacting the source."""
    with pytest.raises(ValueError, match="must be"):
        await ODPAmsterdam().locations(**options)


@pytest.mark.parametrize("capacity", [None, 0, 1.5])
def test_capacity_preserved(capacity: float | None) -> None:
    """Unknown, zero and fractional source estimates must not be conflated."""
    source = feature()
    source["properties"]["aantal"] = capacity
    assert ParkingSpot.from_json(source).number == capacity


@pytest.mark.parametrize("capacity", [True, "1", float("nan"), float("inf")])
def test_invalid_capacity(capacity: Any) -> None:
    """Malformed numeric source values fail explicitly."""
    source = feature()
    source["properties"]["aantal"] = capacity
    with pytest.raises(ODPAmsterdamError):
        ParkingSpot.from_json(source)


def test_regimes_geometry_and_dates() -> None:
    """Keep every restriction and inner ring, without interpreting availability."""
    source = feature()
    regime = deepcopy(source["properties"]["regimes"][0])
    regime.update(
        beginTijd="09:00:00",
        eindTijd="16:00:00",
        dagen=["ma"],
        opmerking="Example",
        beginDatum="2026-09-01",
        eindDatum="2026-10-01",
    )
    source["properties"]["regimes"].append(regime)
    source["properties"]["versiedatum"] = "2026-09-11"
    source["geometry"]["coordinates"].append(
        [[4.8, 52.3], [4.81, 52.3], [4.81, 52.31], [4.8, 52.3]]
    )
    result = ParkingSpot.from_json(source)
    assert result.spot_id == "000123"
    assert result.regimes == source["properties"]["regimes"]
    assert result.geometry == source["geometry"]
    assert result.version_date == date(2026, 9, 11)


@pytest.mark.parametrize("identifier", [None, "", 123])
def test_invalid_identity(identifier: Any) -> None:
    """Do not invent identities from absent or non-string values."""
    source = feature()
    source["properties"]["id"] = identifier
    with pytest.raises(ODPAmsterdamError):
        ParkingSpot.from_json(source)


def test_unknown_regimes_and_date() -> None:
    """An empty regime list and null date remain unknown."""
    source = feature()
    source["properties"].update(regimes=[], versiedatum=None)
    result = ParkingSpot.from_json(source)
    assert result.spot_description is None
    assert result.regimes == []
    assert result.version_date is None


def test_malformed_regimes() -> None:
    """Do not discard an unexpected regime representation."""
    source = feature()
    source["properties"]["regimes"] = [None]
    with pytest.raises(ODPAmsterdamError):
        ParkingSpot.from_json(source)
