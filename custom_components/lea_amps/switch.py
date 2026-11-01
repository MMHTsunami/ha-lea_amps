"""Switch controls for LEA amplifiers."""

from __future__ import annotations

from homeassistant.components.switch import SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import LIMITERS, PATH_AUTO_STANDBY_ENABLE, channel_limiter_path, channel_mute_path
from .coordinator import LeaAmpCoordinator
from .entity import LeaAmpEntity


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up amplifier switches."""
    coordinator: LeaAmpCoordinator = hass.data["lea_amps"][entry.entry_id]
    async_add_entities(
        [
            *(LeaAmpMute(coordinator, channel) for channel in range(1, 5)),
            LeaAmpAutoStandby(coordinator),
            *(
                LeaAmpLimiterSwitch(coordinator, channel, limiter, label)
                for channel in range(1, 5)
                for limiter, label in LIMITERS
            ),
        ]
    )


class LeaAmpLimiterSwitch(LeaAmpEntity, SwitchEntity):
    """Enable or disable a channel limiter."""

    def __init__(
        self, coordinator: LeaAmpCoordinator, channel: int, limiter: str, label: str
    ) -> None:
        super().__init__(coordinator)
        self.channel = channel
        self._label = label
        self._path = channel_limiter_path(channel, limiter, "enable")
        self._attr_unique_id = f"{coordinator.config_entry.entry_id}_channel_{channel}_{limiter}_enable"

    @property
    def name(self) -> str:
        """Return the name based on the channel output name."""
        return f"{self.coordinator.channel_label(self.channel)} {self._label}"

    @property
    def is_on(self) -> bool:
        """Return whether the limiter is enabled."""
        return self.coordinator.data.get(self._path, "").lower() in {"1", "true", "on"}

    async def async_turn_on(self, **kwargs: object) -> None:
        """Enable the limiter."""
        await self.coordinator.client.async_set(self._path, True)

    async def async_turn_off(self, **kwargs: object) -> None:
        """Disable the limiter."""
        await self.coordinator.client.async_set(self._path, False)


class LeaAmpAutoStandby(LeaAmpEntity, SwitchEntity):
    """Control automatic standby."""

    _attr_name = "Auto standby"

    def __init__(self, coordinator: LeaAmpCoordinator) -> None:
        super().__init__(coordinator)
        self._attr_unique_id = f"{coordinator.config_entry.entry_id}_auto_standby"

    @property
    def is_on(self) -> bool:
        """Return whether auto standby is enabled."""
        return self.coordinator.data.get(PATH_AUTO_STANDBY_ENABLE, "").lower() in {
            "1",
            "true",
            "on",
        }

    async def async_turn_on(self, **kwargs: object) -> None:
        """Enable auto standby."""
        await self.coordinator.client.async_set(PATH_AUTO_STANDBY_ENABLE, True)

    async def async_turn_off(self, **kwargs: object) -> None:
        """Disable auto standby."""
        await self.coordinator.client.async_set(PATH_AUTO_STANDBY_ENABLE, False)


class LeaAmpMute(LeaAmpEntity, SwitchEntity):
    """Control a channel output mute."""

    def __init__(self, coordinator: LeaAmpCoordinator, channel: int) -> None:
        super().__init__(coordinator)
        self.channel = channel
        self._attr_unique_id = f"{coordinator.config_entry.entry_id}_channel_{channel}_mute"

    @property
    def name(self) -> str:
        """Return the name based on the channel output name."""
        return f"{self.coordinator.channel_label(self.channel)} mute"

    @property
    def is_on(self) -> bool:
        """Return whether the channel is muted."""
        return self.coordinator.data.get(channel_mute_path(self.channel), "").lower() in {
            "1",
            "true",
            "on",
        }

    @property
    def icon(self) -> str:
        """Return an icon reflecting the mute state."""
        return "mdi:volume-mute" if self.is_on else "mdi:volume-high"

    async def async_turn_on(self, **kwargs: object) -> None:
        """Mute the channel."""
        await self.coordinator.client.async_set(channel_mute_path(self.channel), True)

    async def async_turn_off(self, **kwargs: object) -> None:
        """Unmute the channel."""
        await self.coordinator.client.async_set(channel_mute_path(self.channel), False)
