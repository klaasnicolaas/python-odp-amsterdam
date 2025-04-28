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
from .models import Garage, ParkingSpot

VERSION = metadata.version(__package__)


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
    ) -> Any:
        """Handle a request to the Open Data Platform API of Amsterdam.

        Args:
        ----
            url: The URL to the Open Data Platform API of Amsterdam.
            method: HTTP method to use, for example, 'GET'
            params: Extra options to improve or limit the response.

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

        headers = {
            "Accept": "application/json, text/plain, application/geo+json",
            "User-Agent": f"PythonODPAmsterdam/{VERSION}",
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
                    headers=headers,
                    ssl=True,
                )
                response.raise_for_status()
        except TimeoutError as exception:
            msg = "Timeout occurred while connecting to the Open Data Platform API."
            raise ODPAmsterdamConnectionError(msg) from exception
        except (ClientError, socket.gaierror) as exception:
            msg = "Error occurred while communicating with the Open Data Platform API."
            raise ODPAmsterdamConnectionError(msg) from exception

        types = ["application/json", "text/plain", "application/geo+json"]
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
        limit: int = 10,
        parking_type: str = "",
    ) -> list[ParkingSpot]:
        """Get all the parking locations.

        Args:
        ----
            limit: The number of results to return.
            parking_type: The selected parking type number.

        Returns:
        -------
            A list of ParkingSpot objects.

        """
        locations = await self._request(
            PARKING_SPOT_URL,
            params={"_pageSize": limit, "eType": parking_type, "_format": "geojson"},
        )
        return [ParkingSpot.from_json(item) for item in locations["features"]]

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
