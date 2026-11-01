# GitHub Copilot Instructions: LEA Connect Series Amplifiers Home Assistant Integration

## Project Overview
This project builds a custom Home Assistant integration to monitor and control **LEA Professional Connect Series Amplifiers** using their Open API TCP Protocol over port `4321`.

---

## 1. Configuration & Setup Flow (ConfigFlow)
- **Discovery & Input:** The config flow must prompt the user for the amplifier's **Host / IP Address** (`host`).
- **Default Port:** Pre-fill the default TCP port `4321` (`port`), allowing configuration if needed.
- **Unique ID:** Use the amplifier's serial number or MAC address retrieved during the initial handshake as the unique identifier for the config entry to prevent duplicate setups.

---

## 2. API Communication Architecture
- **Protocol:** TCP text-based protocol communicating on port `4321` (terminated with newline characters `\n`).
- **Command Set Supported:**
  - `GET <path>`: Retrieves current parameter values.
  - `SET <path> <value>`: Modifies control values (e.g., volume, mutes, routing).
  - `SUBSCRIBE <path>`: Registers for asynchronous change notifications for real-time sensor updates and state tracking.
  - `UNSUBSCRIBE <path>`: Cleans up subscriptions on disconnect.
- **Connection Management:** Implement a robust background worker / persistent TCP client reader loop with automatic reconnection logic, exponential backoff, and state synchronization.

---

## 3. Entity Design & Default State Policy
- **Comprehensive Coverage:** Implement sensors and controls for all relevant amplifier telemetry and controls (e.g., channel audio levels in dB, mute states, amplifier temperature, power supply voltage, AC line power usage, fault status, and device metadata).
- **Disabled by Default Policy:** 
  - **CRITICAL:** Every single entity created by this integration **must** have `entity_registry_enabled_default = False` (or `entity_registry_enabled_default: bool = False` in modern Home Assistant entity definitions). 
  - Users can selectively enable the specific channels, meters, or advanced diagnostics they require from the Home Assistant UI after setup, keeping the default device footprint clean.

---

## 4. Coding Standards & Home Assistant Best Practices
- **asyncio-first:** All network I/O and coordination must be asynchronous using Python's `asyncio`.
- **Coordinator Pattern:** Use `DataUpdateCoordinator` combined with TCP subscription push updates to maintain instant state synchronization.
- **Type Hinting:** Fully type-hint all custom integration modules, data coordinators, config entries, and platforms.
- **Translations:** Provide complete English translation strings in `translations/en.json` for config flows, options, and error messages (`cannot_connect`, `invalid_auth`, etc.).
- **Tests:** Structure pytest fixtures to mock TCP socket connections and verify command string formatting (`GET`, `SET`, `SUBSCRIBE`) and responses.