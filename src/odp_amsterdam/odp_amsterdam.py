"""Asynchronous Python client providing Open Data information of Amsterdam."""

from __future__ import annotations

import asyncio
import json
import socket
from dataclasses import dataclass
from importlib import metadata
from typing import Any, Self

from aiohttp import ClientError, ClientSession
from aiohttp.hdrs import METH_GET
from yarl import URL

from .const import FILTER_OUT, PARKING_GARAGE_URL, PARKING_SPOT_URL
from .exceptions import (
    ODPAmsterdamConnectionError,
    ODPAmsterdamError,
    ODPAmsterdamResultsError,
)
from .models import Garage, ParkingLocations, ParkingSpot

VERSION = metadata.version("odp-amsterdam")


@dataclass
class ODPAmsterdam:
    """Main class for handling data fetching from Open Data Platform of Amsterdam."""

    request_timeout: float = 15.0
    session: ClientSession | None = None

    _close_session: bool = False

    async def _request(
        self,
        # uri: str,
        url: str,
        *,
        method: str = METH_GET,
        params: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
    ) -> Any:
        """Handle a request to the Open Data Platform API of Amsterdam.

        Args:
        ----
            url: The URL to the Open Data Platform API of Amsterdam.
            method: HTTP method to use, for example, 'GET'
            params: Extra options to improve or limit the response.
            headers: Request-specific overrides for the default headers.

        Returns:
        -------
            A Python dictionary (text) with the response from
            the Open Data Platform API of Amsterdam.

        Raises:
        ------
            ODPAmsterdamConnectionError: An error occurred while
                communicating with the Open Data Platform API of Amsterdam.
            ODPAmsterdamError: Received an unexpected response from
                the Open Data Platform API of Amsterdam.

        """
        full_url = URL(url)

        request_headers = {
            "Accept": "application/json, text/plain, application/geo+json",
            "User-Agent": f"PythonODPAmsterdam/{VERSION}",
            **(headers or {}),
        }

        if self.session is None:
            self.session = ClientSession()
            self._close_session = True

        try:
            async with asyncio.timeout(self.request_timeout):
                response = await self.session.request(
                    method,
                    full_url,
                    params=params,
                    headers=request_headers,
                    ssl=True,
                )
                response.raise_for_status()
        except TimeoutError as exception:
            msg = "Timeout occurred while connecting to the Open Data Platform API."
            raise ODPAmsterdamConnectionError(msg) from exception
        except (ClientError, socket.gaierror) as exception:
            msg = "Error occurred while communicating with the Open Data Platform API."
            raise ODPAmsterdamConnectionError(msg) from exception

        types = [
            "application/json",
            "application/hal+json",
            "text/plain",
            "application/geo+json",
        ]
        content_type = response.headers.get("Content-Type", "")
        if not any(item in content_type for item in types):
            text = await response.text()
            msg = "Unexpected content type response from the Open Data Platform API"
            raise ODPAmsterdamError(
                msg,
                {"Content-Type": content_type, "response": text},
            )

        return json.loads(await response.text())

    async def locations(
        self,
        limit: int | None = None,
        parking_type: str = "",
        *,
        page_size: int = 1000,
    ) -> ParkingLocations:
        """Retrieve parking records, optionally capped by limit.

        Return records, source total and pages fetched. Inconsistent pages,
        duplicate IDs and changed totals raise ODPAmsterdamError; no partial
        success is returned. A finite limit may return complete=False.
        """
        if limit is not None and (
            isinstance(limit, bool) or not isinstance(limit, int) or limit < 1
        ):
            msg = "limit must be a positive integer or None"
            raise ValueError(msg)
        if (
            isinstance(page_size, bool)
            or not isinstance(page_size, int)
            or not 1 <= page_size <= 1000
        ):
            msg = "page_size must be an integer between 1 and 1000"
            raise ValueError(msg)
        size = min(page_size, limit) if limit is not None else page_size
        records: list[ParkingSpot] = []
        identifiers: set[str] = set()
        total: int | None = None
        page = 1
        while True:
            rows, reported_total = await self._location_page(parking_type, page, size)
            if total is not None and reported_total != total:
                msg = "Parking source total changed during retrieval"
                raise ODPAmsterdamError(msg)
            total = reported_total
            for record in rows:
                if record.spot_id in identifiers:
                    msg = "Duplicate parking source ID during retrieval"
                    raise ODPAmsterdamError(msg)
                identifiers.add(record.spot_id)
                records.append(record)
            target = min(total, limit) if limit is not None else total
            if len(records) >= target:
                break
            page += 1

        # Recheck the selection after the last page, including a limited fetch.
        latest, latest_total = await self._location_page(parking_type, 1, 1)
        if latest_total != total or (
            records
            and (
                latest[0].spot_id != records[0].spot_id
                or latest[0].version_date != records[0].version_date
            )
        ):
            msg = "Parking source changed during retrieval"
            raise ODPAmsterdamError(msg)
        return ParkingLocations(records[:target], total, page)

    async def _location_page(
        self, parking_type: str, page: int, size: int
    ) -> tuple[list[ParkingSpot], int]:
        """Read and validate a counted HAL page from the parking API."""
        data = await self._request(
            PARKING_SPOT_URL,
            headers={
                "Accept": "application/hal+json",
                "Accept-Crs": "EPSG:4326",
            },
            params={
                "_pageSize": size,
                "page": page,
                "eType": parking_type,
                "_count": "true",
                "_format": "json",
                "_sort": "id",
            },
        )
        try:
            info = data["page"]
            total = info["totalElements"]
            rows = data["_embedded"]["parkeervakken"]
            if (
                type(total) is not int
                or total < 0
                or info["number"] != page
                or info["size"] != size
                or not isinstance(rows, list)
                or len(rows) != min(size, max(0, total - (page - 1) * size))
                or bool(data["_links"].get("next")) != (page * size < total)
            ):
                msg = "Invalid or incomplete parking page metadata"
                raise ODPAmsterdamError(msg)
        except (KeyError, TypeError, ValueError) as exception:
            msg = "Invalid or incomplete parking page metadata"
            raise ODPAmsterdamError(msg) from exception
        try:
            records = [
                ParkingSpot.from_json({"properties": row, "geometry": row["geometry"]})
                for row in rows
            ]
        except (KeyError, TypeError, ValueError, IndexError) as exception:
            msg = "Invalid parking record in source response"
            raise ODPAmsterdamError(msg) from exception
        return records, total

    async def all_garages(
        self,
        vehicle: str | None = None,
        category: str | None = None,
    ) -> list[Garage]:
        """Get all the garages.

        Returns
        -------
            A list of Garage objects.

        Raises
        ------
            ODPAmsterdamError: If the data is not valid.

        """
        data = await self._request(PARKING_GARAGE_URL)
        try:
            results: list[Garage] = [
                Garage.from_json(item)
                for item in data["features"]
                if not any(x in item["properties"]["Name"] for x in FILTER_OUT)
            ]
        except KeyError as exception:
            msg = f"Got wrong data from the API: {exception}"
            raise ODPAmsterdamError(msg) from exception

        # Filter on vehicle type and category
        if vehicle:
            results = list(filter(lambda x: x.vehicle == vehicle, results))
        if category:
            results = list(filter(lambda x: x.category == category, results))
        return results

    async def garage(self, garage_id: str) -> Garage:
        """Get info from a single  garage.

        Args:
        ----
            garage_id: The ID of the garage.

        Returns:
        -------
            A garage object.

        Raises:
        ------
            ODPAmsterdamResultsError: When no results are found.

        """
        data = await self._request(PARKING_GARAGE_URL)
        for item in data["features"]:
            if item["Id"] == garage_id:
                return Garage.from_json(item)
        msg = f"No garage was found with id - {garage_id}"
        raise ODPAmsterdamResultsError(msg)

    async def close(self) -> None:
        """Close open client session."""
        if self.session and self._close_session:
            await self.session.close()

    async def __aenter__(self) -> Self:
        """Async enter.

        Returns
        -------
            The Open Data Platform Amsterdam object.

        """
        return self

    async def __aexit__(self, *_exc_info: object) -> None:
        """Async exit.

        Args:
        ----
            _exc_info: Exec type.

        """
        await self.close()
