"""Config flow for SIM7600 4G & GPS Gateway integration."""

from __future__ import annotations

from typing import Any

import serial.tools.list_ports
import voluptuous as vol
from homeassistant import config_entries
from homeassistant.components import usb
from homeassistant.data_entry_flow import FlowResult
from homeassistant.exceptions import HomeAssistantError

from .const import CONF_BAUD_RATE, CONF_SERIAL_PORT, DEFAULT_BAUD, DOMAIN, LOGGER


class Sim7600ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for SIM7600 4G & GPS Gateway."""

    VERSION = 1

    def __init__(self) -> None:
        """Initialize the flow."""
        self._discovery_info: usb.UsbServiceInfo | None = None

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}

        if user_input is not None:
            try:
                await self._validate_input(user_input)
            except CannotConnect:
                errors["base"] = "cannot_connect"
            except Exception:  # pylint: disable=broad-except
                LOGGER.exception("Unexpected exception")
                errors["base"] = "unknown"
            else:
                return self.async_create_entry(
                    title=user_input[CONF_SERIAL_PORT], data=user_input
                )

        ports = await self.hass.async_add_executor_job(serial.tools.list_ports.comports)
        list_of_ports = {
            port.device: f"{port.device} ({port.description})" for port in ports
        }

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_SERIAL_PORT): vol.In(list_of_ports),
                    vol.Required(CONF_BAUD_RATE, default=DEFAULT_BAUD): vol.In(
                        [9600, 19200, 38400, 57600, 115200]
                    ),
                }
            ),
            errors=errors,
        )

    async def async_step_usb(self, discovery_info: usb.UsbServiceInfo) -> FlowResult:
        """Handle USB discovery."""
        LOGGER.debug("USB discovery: %s", discovery_info)

        await self.async_set_unique_id(discovery_info.device)
        self._abort_if_unique_id_configured()

        self._discovery_info = discovery_info
        self.context["title_placeholders"] = {"port": discovery_info.device}
        return await self.async_step_discovery_confirm()

    async def async_step_discovery_confirm(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Confirm discovery."""
        if user_input is not None:
            return self.async_create_entry(
                title=self._discovery_info.device,
                data={
                    CONF_SERIAL_PORT: self._discovery_info.device,
                    CONF_BAUD_RATE: DEFAULT_BAUD,
                },
            )

        self._set_confirm_only()
        return self.async_show_form(
            step_id="discovery_confirm",
            description_placeholders={"port": self._discovery_info.device},
        )

    async def _validate_input(self, data: dict[str, Any]) -> None:
        """Validate the user input allows us to connect.

        Data has the keys from STEP_USER_DATA_SCHEMA with values provided by the user.
        """
        # For now, we just check if we can open the port.
        # In the future, we should send an AT command to verify it's a SIM7600.
        port = data[CONF_SERIAL_PORT]
        baud = data[CONF_BAUD_RATE]

        def _check_port():
            try:
                ser = serial.Serial(port, baud, timeout=1)
                ser.close()
            except Exception as err:
                raise CannotConnect from err

        await self.hass.async_add_executor_job(_check_port)


class CannotConnect(HomeAssistantError):
    """Error to indicate we cannot connect."""
