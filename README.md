# LEA Smart Amp Home Assistant

Custom Home Assistant integration for LEA Professional Connect Series
amplifiers using the local TCP Open API on port `4321`.

The integration follows the [LEA TCP Protocol Rev. 7 (October
2025)](https://leaprofessional.com/wp-content/uploads/2023/02/LEA-TCP-Protocol-rev7-Oct-2025.pdf).

## Functionality

- Connect to an amplifier by host or IP address, with a configurable TCP port (default `4321`).
- Identify the amplifier by its serial number or MAC address to prevent duplicate configuration entries.
- Read amplifier state and receive real-time updates over the local TCP connection.
- Monitor channel audio levels, channel and power-supply status, and AC line measurements.
- Control channel volume and mute, automatic standby, and RMS and peak limiter settings.
- All entities are disabled by default and can be enabled individually in Home Assistant.

## Entities and sensors

### Sensors

- **Per channel (channels 1–4):**
  - Audio level in dBFS, output voltage, and output power
  - Fault, thermal fault, limiting, clipping, signal detected, and ready status
- **Power supply:**
  - AC line voltage, current, and power
  - Fault, thermal, and power OK status

### Controls

- **Per channel (channels 1–4):**
  - Volume and mute
  - RMS limiter and peak limiter enable switches
  - RMS and peak limiter threshold, attack time, and release time
- **Amplifier:**
  - Automatic standby enable, timeout, and signal threshold

## Validated amplifiers

- Connect Series Model 354N
- Connect Series Model 704N
- Connect Series Model 1504N
