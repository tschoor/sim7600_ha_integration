"""Die SIM7600 Integration."""
import voluptuous as vol
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.helpers import config_validation as cv

from .const import CONF_BAUD_RATE, CONF_SERIAL_PORT, DOMAIN
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

    modem = SIM7600Modem(port, baud)
    coordinator = SIM7600DataUpdateCoordinator(hass, modem)

    # Initial data fetch
    await coordinator.async_config_entry_first_refresh()

    hass.data[DOMAIN][entry.entry_id] = {
        "coordinator": coordinator,
        "modem": modem,
    }

    async def handle_send_sms(call: ServiceCall) -> None:
        """Handle the service call."""
        number = call.data.get(ATTR_NUMBER)
        message = call.data.get(ATTR_MESSAGE)
        await modem.send_sms(number, message)

    hass.services.async_register(
        DOMAIN, SERVICE_SEND_SMS, handle_send_sms, schema=SEND_SMS_SCHEMA
    )

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        data = hass.data[DOMAIN].pop(entry.entry_id)
        await data["modem"].disconnect()

    return unload_ok
