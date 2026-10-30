"""Constants for the LEA amplifier integration."""

from __future__ import annotations

from typing import Final

DOMAIN: Final = "lea_amps"
DEFAULT_PORT: Final = 4321
DEFAULT_TIMEOUT: Final = 10.0
CONF_HOST: Final = "host"
CONF_PORT: Final = "port"

ATTR_SERIAL: Final = "serial"
ATTR_MAC: Final = "mac"
ATTR_MODEL: Final = "model"
ATTR_VALUE: Final = "value"

PATH_DEVICE_SERIAL: Final = "/amp/deviceInfo/serialNumber"
PATH_DEVICE_MAC: Final = "/amp/deviceInfo/mac"
PATH_DEVICE_MODEL: Final = "/amp/deviceInfo/modelID"
PATH_DEVICE_NAME: Final = "/amp/deviceInfo/deviceName"
DEFAULT_DEVICE_NAME: Final = "LEA Professional Amplifier"
PATH_POWER_SUPPLY_VOLTAGE: Final = "/amp/powerSupply/acLineVoltage"
PATH_POWER_SUPPLY_CURRENT: Final = "/amp/powerSupply/acLineCurrent"
PATH_POWER_SUPPLY_WATTS: Final = "/amp/powerSupply/acLineWatts"
PATH_POWER_SUPPLY_FAULT: Final = "/amp/powerSupply/fault"
PATH_POWER_SUPPLY_THERMAL: Final = "/amp/powerSupply/thermal"
PATH_POWER_SUPPLY_POWER_OK: Final = "/amp/powerSupply/powerOk"
PATH_AUTO_STANDBY_ENABLE: Final = "/amp/autoStandby/enable"
PATH_AUTO_STANDBY_TIMEOUT: Final = "/amp/autoStandby/timeToWait"
PATH_AUTO_STANDBY_THRESHOLD: Final = "/amp/autoStandby/threshold"


def channel_sensor_path(channel: int, sensor: str) -> str:
    """Return a documented channel sensor path."""
    return f"/amp/channels/{channel}/output/{sensor}"


def channel_level_path(channel: int, level: str) -> str:
    """Return a documented channel level meter path."""
    return f"/amp/channels/{channel}/levels/{level}"


def channel_mute_path(channel: int) -> str:
    """Return the output mute path for a channel."""
    return f"/amp/channels/{channel}/output/mute"


def channel_fader_path(channel: int) -> str:
    """Return the output fader path for a channel."""
    return f"/amp/channels/{channel}/output/fader"


def channel_name_path(channel: int) -> str:
    """Return the output name path for a channel."""
    return f"/amp/channels/{channel}/output/name"


LIMITERS: Final = (("rmsLimiter", "RMS limiter"), ("peakLimiter", "Peak limiter"))


def channel_limiter_path(channel: int, limiter: str, setting: str) -> str:
    """Return a limiter setting path for a channel."""
    return f"/amp/channels/{channel}/{limiter}/{setting}"
