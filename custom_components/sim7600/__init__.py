"""Die SIM7600 Integration."""

import voluptuous as vol
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.helpers import config_validation as cv

from .const import (
    CONF_BAUD_RATE,
    CONF_DEBUG_MODE,
    CONF_SERIAL_PORT,
    DOMAIN,
    LOGGER,
)
from .coordinator import SIM7600DataUpdateCoordinator
from .modem import SIM7600Modem

PLATFORMS: list[Platform] = [Platform.SENSOR, Platform.DEVICE_TRACKER]

SERVICE_SEND_SMS = "send_sms"
ATTR_NUMBER = "number"
ATTR_MESSAGE = "message"

SEND_SMS_SCHEMA = vol.Schema(
    {
        vol.Required(ATTR_NUMBER): cv.string,
        vol.Required(ATTR_MESSAGE): cv.string,
    }
)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Setzt die Integration über die UI (Config Entry) auf."""
    hass.data.setdefault(DOMAIN, {})

    port = entry.data[CONF_SERIAL_PORT]
    baud = entry.data[CONF_BAUD_RATE]
    # Debug-Modus: zuerst options, dann data
    debug = entry.options.get(CONF_DEBUG_MODE, entry.data.get(CONF_DEBUG_MODE, False))

    modem = SIM7600Modem(port, baud, debug=debug)
    coordinator = SIM7600DataUpdateCoordinator(hass, modem, entry)

    await coordinator.async_config_entry_first_refresh()

    hass.data[DOMAIN][entry.entry_id] = {
        "coordinator": coordinator,
        "modem": modem,
    }

    async def handle_send_sms(call: ServiceCall) -> None:
        """Handle the service call."""
        number = call.data.get(ATTR_NUMBER)
        message = call.data.get(ATTR_MESSAGE)
        if isinstance(number, str) and isinstance(message, str):
            await modem.send_sms(number, message)
        else:
            LOGGER.error("Invalid service call data: %s, %s", number, message)

    hass.services.async_register(
        DOMAIN, SERVICE_SEND_SMS, handle_send_sms, schema=SEND_SMS_SCHEMA
    )

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    # Reload-Listener: Änderungen über den Options-Flow übernehmen
    entry.async_on_unload(entry.add_update_listener(_async_reload_entry))

    return True


async def _async_reload_entry(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Lädt die Integration nach Options-Änderungen neu."""
    await hass.config_entries.async_reload(entry.entry_id)


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        data = hass.data[DOMAIN].pop(entry.entry_id)
        await data["modem"].disconnect()

    return unload_ok
