"""Shared entity implementation for LEA amplifiers."""

from __future__ import annotations

from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .coordinator import LeaAmpCoordinator


class LeaAmpEntity(CoordinatorEntity[LeaAmpCoordinator]):
    """Base entity for a LEA amplifier."""

    _attr_entity_registry_enabled_default = False

    def __init__(self, coordinator: LeaAmpCoordinator) -> None:
        super().__init__(coordinator)
        self._attr_device_info = {
            "identifiers": {("lea_amps", coordinator.config_entry.entry_id)},
            "name": coordinator.device_name,
            "manufacturer": "LEA Professional",
        }
