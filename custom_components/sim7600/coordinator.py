"""DataUpdateCoordinator for SIM7600."""

from __future__ import annotations

import time
from datetime import timedelta
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import (
    CONF_DEBUG_MODE,
    CONF_GNSS_INTERVAL,
    CONF_POLLING_INTERVAL,
    DOMAIN,
    LOGGER,
)
from .modem import SIM7600Modem


class SIM7600DataUpdateCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    """Class to manage fetching SIM7600 data."""

    def __init__(
        self, hass: HomeAssistant, modem: SIM7600Modem, entry: ConfigEntry
    ) -> None:
        """Initialize the coordinator."""
        self.polling_interval = entry.data.get(CONF_POLLING_INTERVAL, 60)
        self.gnss_interval = entry.data.get(CONF_GNSS_INTERVAL, 300)
        debug_mode = entry.data.get(CONF_DEBUG_MODE, False)
        self.modem = SIM7600Modem(modem.port, modem.baudrate, debug=debug_mode)
        super().__init__(
            hass,
            LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=self.polling_interval),
        )
        self.imei: str | None = None
        self.firmware: str | None = None
        self.manufacturer: str | None = None
        self.model: str | None = None
        self.last_sms: dict[str, str] | None = None
        self.gps_enabled: bool = False
        self.last_gnss_update: float = 0.0

    async def _async_update_data(self) -> dict[str, Any]:
        """Fetch data from SIM7600."""
        try:
            # Initial retrieval of static system info
            if self.imei is None:
                self.imei = await self.modem.get_imei()
            if self.firmware is None:
                self.firmware = await self.modem.get_firmware()
            if self.manufacturer is None:
                self.manufacturer = await self.modem.get_manufacturer()
            if self.model is None:
                self.model = await self.modem.get_model()

            # Enable GPS once
            if not self.gps_enabled:
                self.gps_enabled = await self.modem.set_gps(True)
                LOGGER.debug("GPS enabled: %s", self.gps_enabled)

            # Periodic polling
            rssi = await self.modem.get_signal_quality()
            operator = await self.modem.get_operator()
            network_info = await self.modem.get_network_info()
            reg_stat = await self.modem.get_registration_status()
            gprs_reg_stat = await self.modem.get_gprs_registration_status()

            # Check for new SMS
            messages = await self.modem.get_unread_sms()
            if messages:
                self.last_sms = messages[-1]

            # Fetch GPS info
            gps_info = None
            now = time.time()
            LOGGER.debug(
                "GPS condition check: enabled=%s, interval=%s, last_update=%s, now=%s",
                self.gps_enabled,
                self.gnss_interval,
                self.last_gnss_update,
                now,
            )
            if self.gps_enabled and (now - self.last_gnss_update > self.gnss_interval):
                gps_info = await self.modem.get_gps_info()
                if gps_info:
                    self.last_gnss_update = now

            # Map RSSI (0-31) to dBm
            signal_dbm = None
            if rssi is not None:
                signal_dbm = -113 + (rssi * 2)

            return {
                "rssi": rssi,
                "signal_dbm": signal_dbm,
                "operator": operator,
                "network_mode": network_info.get("mode"),
                "system_mode": network_info.get("system_mode"),
                "reg_status": reg_stat,
                "gprs_reg_status": gprs_reg_stat,
                "imei": self.imei,
                "firmware": self.firmware,
                "manufacturer": self.manufacturer,
                "model": self.model,
                "last_sms": self.last_sms,
                "gps": gps_info,
            }
        except Exception as err:
            raise UpdateFailed(f"Error communicating with SIM7600: {err}") from err
