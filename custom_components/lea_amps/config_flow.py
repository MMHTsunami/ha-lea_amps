"""Config flow for LEA amplifiers."""

from __future__ import annotations

import asyncio

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.const import CONF_HOST, CONF_PORT
from homeassistant.core import callback

from .api import LeaAmpClient, LeaAmpConnectionError
from .const import DEFAULT_PORT, DOMAIN, PATH_DEVICE_MAC, PATH_DEVICE_SERIAL


class LeaAmpConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a LEA amplifier configuration flow."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, str | int] | None = None
    ) -> config_entries.ConfigFlowResult:
        """Handle the user setup step."""
        errors: dict[str, str] = {}
        if user_input is not None:
            client = LeaAmpClient(
                str(user_input[CONF_HOST]),
                int(user_input[CONF_PORT]),
            )
            try:
                await client.async_connect()
                await client.async_get(PATH_DEVICE_SERIAL)
                unique_id = await asyncio.wait_for(
                    self._async_read_identity(client),
                    client.timeout,
                )
                await client.async_close()
                await self.async_set_unique_id(unique_id)
                self._abort_if_unique_id_configured()
                return self.async_create_entry(
                    title=str(user_input[CONF_HOST]),
                    data=user_input,
                )
            except (LeaAmpConnectionError, asyncio.TimeoutError, OSError):
                errors["base"] = "cannot_connect"
            finally:
                await client.async_close()

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_HOST): str,
                    vol.Required(CONF_PORT, default=DEFAULT_PORT): vol.Coerce(int),
                }
            ),
            errors=errors,
        )

    async def _async_read_identity(self, client: LeaAmpClient) -> str:
        """Read a unique identity from the initial handshake responses."""
        async for message in client.async_messages():
            if message.path in (PATH_DEVICE_SERIAL, PATH_DEVICE_MAC) and message.value:
                return message.value.strip().strip('"')
        raise LeaAmpConnectionError("Amplifier did not provide a serial or MAC address")

    @staticmethod
    @callback
    def async_get_options_flow(
        config_entry: config_entries.ConfigEntry,
    ) -> config_entries.OptionsFlow:
        """Return the options flow."""
        return LeaAmpOptionsFlowHandler(config_entry)


class LeaAmpOptionsFlowHandler(config_entries.OptionsFlow):
    """Handle amplifier options."""

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        self.config_entry = config_entry

    async def async_step_init(
        self, user_input: dict[str, int] | None = None
    ) -> config_entries.ConfigFlowResult:
        """Manage the amplifier port."""
        if user_input is not None:
            return self.async_create_entry(data=user_input)
        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema(
                {vol.Required(CONF_PORT, default=self.config_entry.data[CONF_PORT]): vol.Coerce(int)}
            ),
        )
