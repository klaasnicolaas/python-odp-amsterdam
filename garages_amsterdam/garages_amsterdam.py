"""Asynchronous Python client for the Garages Amsterdam API."""
from __future__ import annotations

import asyncio
import json
from collections.abc import Mapping
from dataclasses import dataclass
from importlib import metadata
from typing import Any

import async_timeout
from aiohttp.client import ClientError, ClientResponseError, ClientSession
from aiohttp.hdrs import METH_GET
from yarl import URL

from .const import WRONGKEYS
from .exceptions import GaragesAmsterdamConnectionError, GaragesAmsterdamError
from .models import Garage


@dataclass
class GaragesAmsterdam:
    """Main class for handling connection with Garages Amsterdam API."""

    request_timeout: float = 10.0
    session: ClientSession | None = None

    _close_session: bool = False

    async def _request(
        self,
        uri: str,
        *,
        method: str = METH_GET,
        params: Mapping[str, str] | None = None,
    ) -> dict[str, Any]:
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
            self.session = ClientSession()
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
        except (ClientError, ClientResponseError) as exception:
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

        return await response.text()

    async def all_garages(self) -> list[Garage]:
        """Get all the garages.

        Returns:
            A list of Garage objects.

        Raises:
            GaragesAmsterdamError: If the data is not valid.
        """
        results = []

        data = await self._request("ParkingLocation.json")
        data = json.loads(data)

        for item in data["features"]:
            try:
                if not any(x in item["properties"]["Name"] for x in WRONGKEYS):
                    results.append(Garage.from_json(item))
            except KeyError as exception:
                raise GaragesAmsterdamError(f"Got wrong data: {item}") from exception
        return results

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

    async def __aexit__(self, *_exc_info) -> None:
        """Async exit.

        Args:
            _exc_info: Exec type.
        """
        await self.close()