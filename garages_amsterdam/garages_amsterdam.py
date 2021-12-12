"""Asynchronous Python client for the Garages Amsterdam API."""
from __future__ import annotations

import asyncio
from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any

from aiohttp.client import ClientError, ClientResponseError, ClientSession
from async_timeout import timeout
from yarl import URL

from .exceptions import GaragesAmsterdamConnectionError, GaragesAmsterdamError
from .models import Garages


@dataclass
class GaragesAmsterdam:
    """Main class for handling connection with Garages Amsterdam API."""

    def __init__(
        self, request_timeout: int = 10, session: ClientSession | None = None
    ) -> None:
        """Initialize connection with the Garages Amsterdam API.

        Args:
            request_timeout: An integer with the request timeout in seconds.
            session: Optional, shared, aiohttp client session.
        """
        self._session = session
        self._close_session: bool = False

        self.request_timeout = request_timeout

    async def request(
        self,
        uri: str,
        *,
        params: Mapping[str, str] | None = None,
    ) -> dict[str, Any]:
        """Handle a request to the Garages Amsterdam API.

        Args:
            uri: Request URI, without '/', for example, 'status'
            params: Extra options to improve or limit the response.

        Returns:
            A Python dictionary (text) with the response from
            the Garages Amsterdam API.

        Raises:
            GaragesAmsterdamConnectionError: An error occurred while
                communicating with the CEMM device.
            GaragesAmsterdamError: Received an unexpected response from
                the CEMM device.
        """
        url = URL("http://opd.it-t.nl/data/amsterdam/").join(URL(uri))

        headers = {
            "Accept": "application/json, text/plain, */*",
        }

        if self._session is None:
            self._session = ClientSession()
            self._close_session = True

        try:
            async with timeout(self.request_timeout):
                response = await self._session.request(
                    "GET",
                    url,
                    params=params,
                    headers=headers,
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

    async def garages(self) -> Garages:
        """Get all the garages.

        Returns:
            A Garages data object from the Garages Amsterdam API.
        """
        data = await self.request("ParkingLocation.json")
        return Garages.from_json(data)

    async def close(self) -> None:
        """Close open client session."""
        if self._session and self._close_session:
            await self._session.close()

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
