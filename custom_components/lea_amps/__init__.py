"""LEA Professional Connect Series amplifier integration."""

from __future__ import annotations

from .const import DOMAIN

async def async_setup_entry(hass: "HomeAssistant", entry: "ConfigEntry") -> bool:
    """Set up a LEA amplifier from a config entry."""
    from homeassistant.config_entries import ConfigEntry
    from homeassistant.const import Platform

    from .coordinator import LeaAmpCoordinator

    platforms = [Platform.SENSOR, Platform.SWITCH, Platform.NUMBER]
    coordinator = LeaAmpCoordinator(hass, entry)
    await coordinator.async_config_entry_first_refresh()
    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = coordinator
    await hass.config_entries.async_forward_entry_setups(entry, platforms)
    return True


async def async_unload_entry(hass: "HomeAssistant", entry: "ConfigEntry") -> bool:
    """Unload a LEA amplifier config entry."""
    from homeassistant.const import Platform

    from .coordinator import LeaAmpCoordinator

    platforms = [Platform.SENSOR, Platform.SWITCH, Platform.NUMBER]
    coordinator: LeaAmpCoordinator = hass.data[DOMAIN].pop(entry.entry_id)
    unloaded = await hass.config_entries.async_unload_platforms(entry, platforms)
    await coordinator.async_shutdown()
    return unloaded
