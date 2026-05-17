"""DataUpdateCoordinator for SIM7600."""

from __future__ import annotations

from datetime import timedelta
from typing import Any

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import DOMAIN, LOGGER
from .modem import SIM7600Modem


class SIM7600DataUpdateCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    """Class to manage fetching SIM7600 data."""

    def __init__(self, hass: HomeAssistant, modem: SIM7600Modem) -> None:
        """Initialize the coordinator."""
        super().__init__(
            hass,
            LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=30),
        )
        self.modem = modem
        self.imei: str | None = None
        self.firmware: str | None = None
        self.last_sms: dict[str, str] | None = None
        self.gps_enabled: bool = False

    async def _async_update_data(self) -> dict[str, Any]:
        """Fetch data from SIM7600."""
        try:
            # Fetch static info once
            if self.imei is None:
                self.imei = await self.modem.get_imei()
            if self.firmware is None:
                self.firmware = await self.modem.get_firmware()

            # Enable GPS once
            if not self.gps_enabled:
                self.gps_enabled = await self.modem.set_gps(True)

            rssi = await self.modem.get_signal_quality()
            operator = await self.modem.get_operator()
            network_info = await self.modem.get_network_info()
            sim_status = await self.modem.get_sim_status()

            # Check for new SMS
            messages = await self.modem.get_unread_sms()
            if messages:
                self.last_sms = messages[-1]

            # Fetch GPS info
            gps_info = None
            if self.gps_enabled:
                gps_info = await self.modem.get_gps_info()

            # Map RSSI (0-31) to dBm
            # 0: -113 dBm, 31: -51 dBm, 1 unit = 2 dBm
            signal_dbm = None
            if rssi is not None:
                signal_dbm = -113 + (rssi * 2)

            return {
                "rssi": rssi,
                "signal_dbm": signal_dbm,
                "operator": operator,
                "network_mode": network_info.get("mode"),
                "system_mode": network_info.get("system_mode"),
                "sim_status": sim_status,
                "imei": self.imei,
                "firmware": self.firmware,
                "last_sms": self.last_sms,
                "gps": gps_info,
            }
        except Exception as err:
            raise UpdateFailed(f"Error communicating with SIM7600: {err}") from err
