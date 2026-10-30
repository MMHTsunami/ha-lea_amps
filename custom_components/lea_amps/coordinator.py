"""Data coordinator for LEA amplifiers."""

from __future__ import annotations

import asyncio
import logging
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import LeaAmpClient, LeaAmpConnectionError
from .const import (
    CONF_HOST,
    CONF_PORT,
    DEFAULT_DEVICE_NAME,
    DOMAIN,
    LIMITERS,
    PATH_DEVICE_NAME,
    channel_limiter_path,
    channel_fader_path,
    channel_level_path,
    channel_mute_path,
    channel_name_path,
    channel_sensor_path,
    PATH_DEVICE_MODEL,
    PATH_DEVICE_SERIAL,
    PATH_POWER_SUPPLY_CURRENT,
    PATH_POWER_SUPPLY_FAULT,
    PATH_POWER_SUPPLY_THERMAL,
    PATH_POWER_SUPPLY_VOLTAGE,
    PATH_POWER_SUPPLY_WATTS,
    PATH_POWER_SUPPLY_POWER_OK,
    PATH_AUTO_STANDBY_ENABLE,
    PATH_AUTO_STANDBY_TIMEOUT,
    PATH_AUTO_STANDBY_THRESHOLD,
)

_LOGGER = logging.getLogger(__name__)
_INITIAL_PATHS = (
    PATH_DEVICE_SERIAL,
    PATH_DEVICE_MODEL,
    PATH_POWER_SUPPLY_CURRENT,
    PATH_POWER_SUPPLY_FAULT,
    PATH_POWER_SUPPLY_THERMAL,
    PATH_POWER_SUPPLY_VOLTAGE,
    PATH_POWER_SUPPLY_WATTS,
    PATH_POWER_SUPPLY_POWER_OK,
    PATH_AUTO_STANDBY_ENABLE,
    PATH_AUTO_STANDBY_TIMEOUT,
    PATH_AUTO_STANDBY_THRESHOLD,
    *(channel_name_path(channel) for channel in range(1, 5)),
    *(
        channel_limiter_path(channel, limiter, setting)
        for channel in range(1, 5)
        for limiter, _ in LIMITERS
        for setting in ("enable", "threshold", "attackTime", "releaseTime")
    ),
    *(channel_mute_path(channel) for channel in range(1, 5)),
    *(channel_fader_path(channel) for channel in range(1, 5)),
    *(
        channel_sensor_path(channel, sensor)
        for channel in range(1, 5)
        for sensor in ("fault", "thermal", "limiting", "clip", "signalDetect", "ready")
    ),
    *(
        channel_level_path(channel, level)
        for channel in range(1, 5)
        for level in ("level_db", "level_volts", "level_watts")
    ),
)


class LeaAmpCoordinator(DataUpdateCoordinator[dict[str, str]]):
    """Coordinate polling and push updates from an amplifier."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        self.config_entry = entry
        self.client = LeaAmpClient(
            entry.data[CONF_HOST],
            entry.data[CONF_PORT],
        )
        self._message_task: asyncio.Task[None] | None = None
        self._initial_data: dict[str, str] = {}
        self.device_name = DEFAULT_DEVICE_NAME
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_method=self._async_update_data,
        )

    async def _async_update_data(self) -> dict[str, str]:
        """Connect and request the initial state."""
        try:
            if self.client._writer is None:
                await self.client.async_connect()
            if self._message_task is None:
                await self._async_load_device_name()
                await self._async_load_channel_names()
            for path in _INITIAL_PATHS:
                await self.client.async_get(path)
                await self.client.async_subscribe(path)
            if self._message_task is None:
                self._message_task = asyncio.create_task(self._async_read_messages())
            return {**self._initial_data, **(self.data or {})}
        except LeaAmpConnectionError as err:
            raise UpdateFailed(str(err)) from err

    def channel_label(self, channel: int) -> str:
        """Return the configured output name for a channel."""
        name = (self.data or {}).get(channel_name_path(channel), "").strip().strip('"')
        return name or f"Channel {channel}"

    async def _async_load_channel_names(self) -> None:
        """Query channel output names before entities are created."""
        pending = {channel_name_path(channel) for channel in range(1, 5)}

        async def _read_names() -> None:
            async for message in self.client.async_messages():
                if message.path in pending:
                    self._initial_data[message.path] = message.value
                    pending.discard(message.path)
                    if not pending:
                        return

        for path in tuple(pending):
            await self.client.async_get(path)
        try:
            await asyncio.wait_for(_read_names(), self.client.timeout)
        except asyncio.TimeoutError:
            _LOGGER.debug("Timed out reading channel output names")

    async def _async_load_device_name(self) -> None:
        """Query the configured device name before entities are created."""

        async def _read_name() -> str | None:
            async for message in self.client.async_messages():
                if message.path == PATH_DEVICE_NAME:
                    return message.value.strip().strip('"')
            return None

        await self.client.async_get(PATH_DEVICE_NAME)
        try:
            name = await asyncio.wait_for(_read_name(), self.client.timeout)
        except asyncio.TimeoutError:
            _LOGGER.debug("Timed out reading amplifier device name")
            return
        if name:
            self.device_name = name

    async def _async_read_messages(self) -> None:
        """Apply asynchronous protocol notifications to coordinator data."""
        try:
            async for message in self.client.async_messages():
                self.async_set_updated_data(
                    {**(self.data or {}), message.path: message.value}
                )
        except (LeaAmpConnectionError, ConnectionError) as err:
            _LOGGER.warning("Lost connection to amplifier: %s", err)

    async def async_shutdown(self) -> None:
        """Stop the reader and close the connection."""
        if self._message_task is not None:
            self._message_task.cancel()
            await asyncio.gather(self._message_task, return_exceptions=True)
        await self.client.async_close()
