"""Asynchronous TCP client for the LEA amplifier text protocol."""

from __future__ import annotations

import asyncio
from collections.abc import AsyncIterator
from dataclasses import dataclass

from .const import DEFAULT_TIMEOUT


class LeaAmpConnectionError(Exception):
    """Raised when an amplifier connection cannot be established."""


@dataclass(frozen=True, slots=True)
class LeaAmpMessage:
    """A parsed protocol response or notification."""

    path: str
    value: str


class LeaAmpClient:
    """Maintain an asynchronous newline-delimited amplifier connection."""

    def __init__(self, host: str, port: int, timeout: float = DEFAULT_TIMEOUT) -> None:
        self.host = host
        self.port = port
        self.timeout = timeout
        self._reader: asyncio.StreamReader | None = None
        self._writer: asyncio.StreamWriter | None = None

    async def async_connect(self) -> None:
        """Connect to the amplifier."""
        try:
            self._reader, self._writer = await asyncio.wait_for(
                asyncio.open_connection(self.host, self.port),
                timeout=self.timeout,
            )
        except (OSError, asyncio.TimeoutError) as err:
            raise LeaAmpConnectionError(
                f"Unable to connect to {self.host}:{self.port}"
            ) from err

    async def async_close(self) -> None:
        """Close the current connection."""
        if self._writer is None:
            return
        self._writer.close()
        await self._writer.wait_closed()
        self._reader = None
        self._writer = None

    async def async_command(self, command: str) -> None:
        """Send one protocol command."""
        if self._writer is None:
            raise LeaAmpConnectionError("Amplifier is not connected")
        self._writer.write(f"{command}\n".encode())
        await self._writer.drain()

    async def async_get(self, path: str) -> None:
        """Request a value from the amplifier."""
        await self.async_command(f"GET {self._format_path(path)}")

    async def async_set(self, path: str, value: str | int | float | bool) -> None:
        """Set a value on the amplifier."""
        await self.async_command(f"SET {self._format_path(path)} {value}")

    async def async_subscribe(self, path: str) -> None:
        """Subscribe to value changes."""
        await self.async_command(f"SUBSCRIBE {self._format_path(path)}")

    async def async_unsubscribe(self, path: str) -> None:
        """Remove a value subscription."""
        await self.async_command(f"UNSUBSCRIBE {self._format_path(path)}")

    @staticmethod
    def _format_path(path: str) -> str:
        """Return a protocol path with the required leading slash."""
        return f"/{path.lstrip('/')}"

    async def async_messages(self) -> AsyncIterator[LeaAmpMessage]:
        """Yield parsed messages until the connection closes."""
        if self._reader is None:
            raise LeaAmpConnectionError("Amplifier is not connected")
        while line := await self._reader.readline():
            text = line.decode(errors="replace").strip()
            if not text:
                continue
            path, separator, value = text.partition(" ")
            if not separator:
                continue
            yield LeaAmpMessage(path, value)
