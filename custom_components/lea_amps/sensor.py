"""Sensors for LEA amplifiers."""

from __future__ import annotations

from dataclasses import dataclass
import logging

from homeassistant.components.sensor import SensorDeviceClass, SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    UnitOfElectricCurrent,
    UnitOfElectricPotential,
    UnitOfPower,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import (
    PATH_POWER_SUPPLY_CURRENT,
    PATH_POWER_SUPPLY_FAULT,
    PATH_POWER_SUPPLY_THERMAL,
    PATH_POWER_SUPPLY_VOLTAGE,
    PATH_POWER_SUPPLY_WATTS,
    PATH_POWER_SUPPLY_POWER_OK,
    channel_level_path,
    channel_sensor_path,
)
from .coordinator import LeaAmpCoordinator
from .entity import LeaAmpEntity

_LOGGER = logging.getLogger(__name__)


@dataclass(frozen=True, slots=True)
class SensorDescription:
    """Describe a LEA amplifier sensor."""

    key: str
    name: str
    path: str
    unit: str | None = None
    device_class: SensorDeviceClass | None = None
    numeric: bool = False
    channel: int | None = None

def _channel_descriptions(channel: int) -> tuple[SensorDescription, ...]:
    """Return documented sensors for one amplifier channel."""
    prefix = f"Channel {channel}"
    return (
        SensorDescription(
            f"channel_{channel}_level_db",
            f"{prefix} level",
            channel_level_path(channel, "level_db"),
            "dBFS",
            numeric=True,
            channel=channel,
        ),
        SensorDescription(
            f"channel_{channel}_level_volts",
            f"{prefix} voltage",
            channel_level_path(channel, "level_volts"),
            UnitOfElectricPotential.VOLT,
            SensorDeviceClass.VOLTAGE,
            True,
            channel,
        ),
        SensorDescription(
            f"channel_{channel}_level_watts",
            f"{prefix} power",
            channel_level_path(channel, "level_watts"),
            UnitOfPower.WATT,
            SensorDeviceClass.POWER,
            True,
            channel,
        ),
        *(
            SensorDescription(
                f"channel_{channel}_{sensor}",
                f"{prefix} {label}",
                channel_sensor_path(channel, sensor),
                channel=channel,
            )
            for sensor, label in (
                ("fault", "fault"),
                ("thermal", "thermal fault"),
                ("limiting", "limiting"),
                ("clip", "clip"),
                ("signalDetect", "signal detected"),
                ("ready", "ready"),
            )
        ),
    )


DESCRIPTIONS: tuple[SensorDescription, ...] = (
    SensorDescription(
        "power_supply_voltage",
        "AC line voltage",
        PATH_POWER_SUPPLY_VOLTAGE,
        UnitOfElectricPotential.VOLT,
        SensorDeviceClass.VOLTAGE,
        True,
    ),
    SensorDescription(
        "power_supply_current",
        "AC line current",
        PATH_POWER_SUPPLY_CURRENT,
        UnitOfElectricCurrent.AMPERE,
        SensorDeviceClass.CURRENT,
        True,
    ),
    SensorDescription(
        "power_supply_watts",
        "AC line power",
        PATH_POWER_SUPPLY_WATTS,
        UnitOfPower.WATT,
        SensorDeviceClass.POWER,
        True,
    ),
    SensorDescription("power_supply_fault", "Power supply fault", PATH_POWER_SUPPLY_FAULT),
    SensorDescription("power_supply_thermal", "Power supply thermal", PATH_POWER_SUPPLY_THERMAL),
    SensorDescription("power_supply_power_ok", "Power supply OK", PATH_POWER_SUPPLY_POWER_OK),
) + tuple(
    description
    for channel in range(1, 5)
    for description in _channel_descriptions(channel)
)


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up amplifier sensors."""
    coordinator: LeaAmpCoordinator = hass.data["lea_amps"][entry.entry_id]
    _LOGGER.warning("Registering %d amplifier sensors", len(DESCRIPTIONS))
    async_add_entities(LeaAmpSensor(coordinator, description) for description in DESCRIPTIONS)


class LeaAmpSensor(LeaAmpEntity, SensorEntity):
    """Represent a LEA amplifier sensor."""

    def __init__(self, coordinator: LeaAmpCoordinator, description: SensorDescription) -> None:
        super().__init__(coordinator)
        self._description = description
        self._attr_name = description.name
        self._attr_unique_id = f"{coordinator.config_entry.entry_id}_{description.key}"
        self._attr_device_class = description.device_class
        self._attr_native_unit_of_measurement = description.unit

    @property
    def name(self) -> str:
        """Return the name, prefixed by the channel output name if applicable."""
        if self._description.channel is None:
            return self._description.name
        label = self.coordinator.channel_label(self._description.channel)
        return self._description.name.replace(
            f"Channel {self._description.channel}", label, 1
        )

    @property
    def native_value(self) -> float | str | None:
        """Return the current value."""
        value = self.coordinator.data.get(self._description.path)
        if value is None:
            return None
        if self._description.numeric:
            try:
                return float(value)
            except ValueError:
                return None
        return value
