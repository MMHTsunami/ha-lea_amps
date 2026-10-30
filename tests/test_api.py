"""Tests for the LEA amplifier protocol client."""

from __future__ import annotations

import asyncio

import pytest

from custom_components.lea_amps.api import LeaAmpClient


@pytest.mark.asyncio
async def test_commands_are_newline_terminated() -> None:
    """Commands use the documented text protocol."""
    received: list[str] = []

    async def handle(
        reader: asyncio.StreamReader, writer: asyncio.StreamWriter
    ) -> None:
        for _ in range(4):
            received.append((await reader.readline()).decode().strip())
        writer.close()
        await writer.wait_closed()

    server = await asyncio.start_server(handle, "127.0.0.1", 0)
    port = server.sockets[0].getsockname()[1]
    client = LeaAmpClient("127.0.0.1", port)
    await client.async_connect()
    await client.async_get("amp/device/serial")
    await client.async_set("amp/channels/1/output/mute", True)
    await client.async_subscribe("amp/device/temperature")
    await client.async_unsubscribe("amp/device/temperature")
    await asyncio.sleep(0)
    await client.async_close()
    server.close()
    await server.wait_closed()

    assert received == [
        "GET /amp/device/serial",
        "SET /amp/channels/1/output/mute True",
        "SUBSCRIBE /amp/device/temperature",
        "UNSUBSCRIBE /amp/device/temperature",
    ]
