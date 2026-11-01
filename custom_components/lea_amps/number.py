"""Number controls for LEA amplifiers."""

from __future__ import annotations

from homeassistant.components.number import NumberEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import UnitOfTime
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import (
    LIMITERS,
    PATH_AUTO_STANDBY_THRESHOLD,
    PATH_AUTO_STANDBY_TIMEOUT,
    channel_fader_path,
    channel_limiter_path,
)
from .coordinator import LeaAmpCoordinator
from .entity import LeaAmpEntity

# (setting, label, unit, min, max, step)
_LIMITER_SETTINGS = (
    ("threshold", "threshold", "V", 0.0, 400.0, 0.1),
    ("attackTime", "attack", UnitOfTime.MILLISECONDS, 0.0, 60000.0, 1.0),
    ("releaseTime", "release", UnitOfTime.MILLISECONDS, 0.0, 60000.0, 1.0),
)


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up amplifier number controls."""
    coordinator: LeaAmpCoordinator = hass.data["lea_amps"][entry.entry_id]
    async_add_entities(
        [
            *(LeaAmpVolume(coordinator, channel) for channel in range(1, 5)),
            LeaAmpAutoStandbyTimeout(coordinator),
            LeaAmpAutoStandbyThreshold(coordinator),
            *(
                LeaAmpLimiterNumber(coordinator, channel, limiter, limiter_label, *setting)
                for channel in range(1, 5)
                for limiter, limiter_label in LIMITERS
                for setting in _LIMITER_SETTINGS
            ),
        ]
    )


class LeaAmpLimiterNumber(LeaAmpEntity, NumberEntity):
    """Control a channel limiter setting."""

    def __init__(
        self,
        coordinator: LeaAmpCoordinator,
        channel: int,
        limiter: str,
        limiter_label: str,
        setting: str,
        label: str,
        unit: str,
        minimum: float,
        maximum: float,
        step: float,
    ) -> None:
        super().__init__(coordinator)
        self.channel = channel
        self._label = f"{limiter_label} {label}"
        self._path = channel_limiter_path(channel, limiter, setting)
        self._attr_native_unit_of_measurement = unit
        self._attr_native_min_value = minimum
        self._attr_native_max_value = maximum
        self._attr_native_step = step
        self._attr_unique_id = (
            f"{coordinator.config_entry.entry_id}_channel_{channel}_{limiter}_{setting}"
        )

    @property
    def name(self) -> str:
        """Return the name based on the channel output name."""
        return f"{self.coordinator.channel_label(self.channel)} {self._label}"

    @property
    def native_value(self) -> float | None:
        """Return the current setting."""
        value = self.coordinator.data.get(self._path)
        try:
            return float(value) if value is not None else None
        except ValueError:
            return None

    async def async_set_native_value(self, value: float) -> None:
        """Set the limiter value."""
        await self.coordinator.client.async_set(self._path, value)


class LeaAmpAutoStandbyThreshold(LeaAmpEntity, NumberEntity):
    """Control the auto standby signal threshold."""

    _attr_name = "Auto standby threshold"
    _attr_native_min_value = -80.0
    _attr_native_max_value = 0.0
    _attr_native_step = 1.0
    _attr_native_unit_of_measurement = "dB"

    def __init__(self, coordinator: LeaAmpCoordinator) -> None:
        super().__init__(coordinator)
        self._attr_unique_id = f"{coordinator.config_entry.entry_id}_auto_standby_threshold"

    @property
    def native_value(self) -> float | None:
        """Return the threshold in dB."""
        value = self.coordinator.data.get(PATH_AUTO_STANDBY_THRESHOLD)
        return float(value) if value is not None else None

    async def async_set_native_value(self, value: float) -> None:
        """Set the threshold in dB."""
        await self.coordinator.client.async_set(PATH_AUTO_STANDBY_THRESHOLD, int(value))


class LeaAmpAutoStandbyTimeout(LeaAmpEntity, NumberEntity):
    """Control the auto standby timeout."""

    _attr_name = "Auto standby timeout"
    _attr_native_min_value = 1
    _attr_native_max_value = 3600
    _attr_native_step = 1
    _attr_native_unit_of_measurement = UnitOfTime.SECONDS

    def __init__(self, coordinator: LeaAmpCoordinator) -> None:
        super().__init__(coordinator)
        self._attr_unique_id = f"{coordinator.config_entry.entry_id}_auto_standby_timeout"

    @property
    def native_value(self) -> float | None:
        """Return the timeout in seconds."""
        value = self.coordinator.data.get(PATH_AUTO_STANDBY_TIMEOUT)
        return float(value) if value is not None else None

    async def async_set_native_value(self, value: float) -> None:
        """Set the timeout in seconds."""
        await self.coordinator.client.async_set(PATH_AUTO_STANDBY_TIMEOUT, int(value))


class LeaAmpVolume(LeaAmpEntity, NumberEntity):
    """Control a channel output fader."""

    _attr_native_min_value = -80.0
    _attr_native_max_value = 0.0
    _attr_native_step = 0.1

    def __init__(self, coordinator: LeaAmpCoordinator, channel: int) -> None:
        super().__init__(coordinator)
        self.channel = channel
        self._attr_unique_id = f"{coordinator.config_entry.entry_id}_channel_{channel}_volume"

    @property
    def name(self) -> str:
        """Return the name based on the channel output name."""
        return f"{self.coordinator.channel_label(self.channel)} volume"

    @property
    def native_value(self) -> float | None:
        """Return the current volume."""
        value = self.coordinator.data.get(channel_fader_path(self.channel))
        return float(value) if value is not None else None

    async def async_set_native_value(self, value: float) -> None:
        """Set the channel output fader."""
        await self.coordinator.client.async_set(channel_fader_path(self.channel), value)
