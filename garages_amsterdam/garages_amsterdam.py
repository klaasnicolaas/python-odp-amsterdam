"""Asynchronous Python client for the Garages Amsterdam API."""
from __future__ import annotations

import asyncio
import json
import socket
from dataclasses import dataclass
from importlib import metadata
from typing import Any

import aiohttp
import async_timeout
from aiohttp import hdrs
from yarl import URL

from .const import WRONGKEYS
from .exceptions import (
    GaragesAmsterdamConnectionError,
    GaragesAmsterdamError,
    GaragesAmsterdamResultsError,
)
from .models import Garage


@dataclass
class GaragesAmsterdam:
    """Main class for handling connection with Garages Amsterdam API."""

    request_timeout: float = 10.0
    session: aiohttp.client.ClientSession | None = None

    _close_session: bool = False

    async def _request(
        self,
        uri: str,
        *,
        method: str = hdrs.METH_GET,
        params: dict[str, Any] | None = None,
    ) -> Any:
        """Handle a request to the Garages Amsterdam API.

        Args:
            uri: Request URI, without '/', for example, 'status'
            method: HTTP method to use, for example, 'GET'
            params: Extra options to improve or limit the response.

        Returns:
            A Python dictionary (text) with the response from
            the Garages Amsterdam API.

        Raises:
            GaragesAmsterdamConnectionError: An error occurred while
                communicating with the Garages Amsterdam API.
            GaragesAmsterdamError: Received an unexpected response from
                the Garages Amsterdam API.
        """
        version = metadata.version(__package__)
        url = URL.build(
            scheme="http", host="opd.it-t.nl", path="/data/amsterdam/"
        ).join(URL(uri))

        headers = {
            "Accept": "application/json, text/plain",
            "User-Agent": f"PythonGaragesAmsterdam/{version}",
        }

        if self.session is None:
            self.session = aiohttp.ClientSession()
            self._close_session = True

        try:
            async with async_timeout.timeout(self.request_timeout):
                response = await self.session.request(
                    method,
                    url,
                    params=params,
                    headers=headers,
                    ssl=False,
                )
                response.raise_for_status()
        except asyncio.TimeoutError as exception:
            raise GaragesAmsterdamConnectionError(
                "Timeout occurred while connecting to the Garages Amsterdam API.",
            ) from exception
        except (aiohttp.ClientError, socket.gaierror) as exception:
            raise GaragesAmsterdamConnectionError(
                "Error occurred while communicating with the Garages Amsterdam API."
            ) from exception

        content_type = response.headers.get("Content-Type", "")
        if "text/plain" not in content_type:
            text = await response.text()
            raise GaragesAmsterdamError(
                "Unexpected response from the Garages Amsterdam API",
                {"Content-Type": content_type, "response": text},
            )

        return json.loads(await response.text())

    async def all_garages(self) -> list[Garage]:
        """Get all the garages.

        Returns:
            A list of Garage objects.

        Raises:
            GaragesAmsterdamError: If the data is not valid.
        """
        results: list[Garage] = []
        data = await self._request("ParkingLocation.json")

        for item in data["features"]:
            try:
                if not any(x in item["properties"]["Name"] for x in WRONGKEYS):
                    results.append(Garage.from_json(item))
            except KeyError as exception:
                raise GaragesAmsterdamError(f"Got wrong data: {item}") from exception
        return results

    async def garage(self, garage_id: str) -> Garage:
        """Get info from a single parking garage.

        Args:
            garage_id: The ID of the garage.

        Returns:
            A garage object.

        Raises:
            GaragesAmsterdamResultsError: When no results are found.
        """
        data = await self._request("ParkingLocation.json")
        try:
            result = [item for item in data["features"] if item["Id"] in garage_id]
            return Garage.from_json(result[0])
        except IndexError as exception:
            raise GaragesAmsterdamResultsError(
                f"No garage was found with id ({garage_id})"
            ) from exception

    async def close(self) -> None:
        """Close open client session."""
        if self.session and self._close_session:
            await self.session.close()

    async def __aenter__(self) -> GaragesAmsterdam:
        """Async enter.

        Returns:
            The Garages Amsterdam object.
        """
        return self

    async def __aexit__(self, *_exc_info: str) -> None:
        """Async exit.

        Args:
            _exc_info: Exec type.
        """
        await self.close()
