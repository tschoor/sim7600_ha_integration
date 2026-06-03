"""DataUpdateCoordinator for SIM7600."""

from __future__ import annotations

import time
from datetime import timedelta
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import (
    CONF_GNSS_INTERVAL,
    CONF_POLLING_INTERVAL,
    DEFAULT_GNSS_INTERVAL,
    DEFAULT_POLLING_INTERVAL,
    DOMAIN,
    LOGGER,
)
from .modem import SIM7600Modem
from .types import GpsData, SmsData


class SIM7600DataUpdateCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    """Class to manage fetching SIM7600 data.

    Eigensteuerungslogik:
    - Statische Daten (IMEI, Firmware, Hersteller, Modell) werden einmalig gecacht.
    - GPS wird separat mit gnss_interval abgefragt.
    - State-Persistenz: Letzte bekannte Werte bleiben bei None-Antworten erhalten.
    - UpdateFailed wird nur bei Verbindungsausfall (Exception) geworfen.
    - GPS-Aktivierung wird bei Fehler in jedem Zyklus erneut versucht.
    - SMS werden nach dem Auslesen aus dem Modem-Speicher gelöscht.
    """

    def __init__(
        self, hass: HomeAssistant, modem: SIM7600Modem, entry: ConfigEntry
    ) -> None:
        """Initialize the coordinator."""
        # Polling-Interval: zuerst entry.options, dann entry.data, dann Standardwert
        self.polling_interval: int = entry.options.get(
            CONF_POLLING_INTERVAL
        ) or entry.data.get(CONF_POLLING_INTERVAL, DEFAULT_POLLING_INTERVAL)
        self.gnss_interval: int = entry.options.get(
            CONF_GNSS_INTERVAL
        ) or entry.data.get(CONF_GNSS_INTERVAL, DEFAULT_GNSS_INTERVAL)
        self.modem = modem
        super().__init__(
            hass,
            LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=self.polling_interval),
        )

        # Statische Daten — einmalig gecacht, bleiben bis Integration neu startet
        self.imei: str | None = None
        self.firmware: str | None = None
        self.manufacturer: str | None = None
        self.model: str | None = None

        # GPS-Steuerung
        self.gps_enabled: bool = False
        self.last_gnss_update: float = 0.0

        # Fehler-Tracking für Spec 6.5: WARNING nach >3 aufeinanderfolgenden Fehlern
        self._consecutive_failures: int = 0

        # State-Persistenz: letzte bekannte Werte (bleiben bei None-Antworten erhalten)
        self._cached_rssi: int | None = None
        self._cached_signal_dbm: float | None = None
        self._cached_operator: str | None = None
        self._cached_network_mode: str | None = None
        self._cached_system_mode: str | None = None
        self._cached_reg_status: int | None = None
        self._cached_gprs_reg_status: int | None = None
        self._cached_sim_status: str | None = None
        self._cached_gps: GpsData | None = None
        self._cached_last_sms: SmsData | None = None

    async def _async_update_data(self) -> dict[str, Any]:
        """Fetch data from SIM7600.

        Fehlerbehandlung:
        - Exception → UpdateFailed (HA markiert Entities unavailable).
        - None-Antwort einzelner AT-Befehle → kein Fehler, letzter Wert bleibt.
        """
        try:
            # Statische Systeminfo — einmalig abrufen, danach permanent gecacht
            if self.imei is None:
                self.imei = await self.modem.get_imei()
            if self.firmware is None:
                self.firmware = await self.modem.get_firmware()
            if self.manufacturer is None:
                self.manufacturer = await self.modem.get_manufacturer()
            if self.model is None:
                self.model = await self.modem.get_model()

            # GPS aktivieren; bei False erneut im nächsten Zyklus versuchen
            if not self.gps_enabled:
                self.gps_enabled = await self.modem.set_gps(True)
                LOGGER.debug("GPS enabled: %s", self.gps_enabled)

            # Dynamische Netzwerkdaten — State-Persistenz: neuer Wert überschreibt Cache
            new_rssi = await self.modem.get_signal_quality()
            if new_rssi is not None:
                self._cached_rssi = new_rssi
                self._cached_signal_dbm = -113 + (new_rssi * 2)

            new_operator = await self.modem.get_operator()
            if new_operator is not None:
                self._cached_operator = new_operator

            network_info = await self.modem.get_network_info()
            if network_info.get("mode") is not None:
                self._cached_network_mode = network_info["mode"]
            if network_info.get("system_mode") is not None:
                self._cached_system_mode = network_info["system_mode"]

            new_reg = await self.modem.get_registration_status()
            if new_reg is not None:
                self._cached_reg_status = new_reg

            new_gprs_reg = await self.modem.get_gprs_registration_status()
            if new_gprs_reg is not None:
                self._cached_gprs_reg_status = new_gprs_reg

            new_sim_status = await self.modem.get_sim_status()
            if new_sim_status is not None:
                self._cached_sim_status = new_sim_status

            # SMS abrufen und nach dem Lesen löschen (verhindert Speicherüberlauf)
            messages = await self.modem.get_unread_sms()
            if messages:
                self._cached_last_sms = messages[-1]
                for sms in messages:
                    await self.modem.delete_sms(sms.index)

            # GNSS — zeitgesteuert mit gnss_interval
            now = time.time()
            LOGGER.debug(
                "GPS condition check: enabled=%s, interval=%s, last_update=%s, now=%s",
                self.gps_enabled,
                self.gnss_interval,
                self.last_gnss_update,
                now,
            )
            if self.gps_enabled and (now - self.last_gnss_update > self.gnss_interval):
                new_gps = await self.modem.get_gps_info()
                if new_gps is not None:
                    self._cached_gps = new_gps
                    self.last_gnss_update = now
                    LOGGER.info(
                        "GPS fix: lat=%.6f, lon=%.6f",
                        new_gps.latitude,
                        new_gps.longitude,
                    )

            self._consecutive_failures = 0
            return {
                "rssi": self._cached_rssi,
                "signal_dbm": self._cached_signal_dbm,
                "operator": self._cached_operator,
                "network_mode": self._cached_network_mode,
                "system_mode": self._cached_system_mode,
                "reg_status": self._cached_reg_status,
                "gprs_reg_status": self._cached_gprs_reg_status,
                "imei": self.imei,
                "firmware": self.firmware,
                "manufacturer": self.manufacturer,
                "model": self.model,
                "sim_status": self._cached_sim_status,
                "last_sms": self._cached_last_sms,
                "gps": self._cached_gps,
            }
        except Exception as err:
            self._consecutive_failures += 1
            if self._consecutive_failures > 3:
                LOGGER.warning(
                    "SIM7600 unreachable for %d consecutive update cycles",
                    self._consecutive_failures,
                )
            raise UpdateFailed(f"Error communicating with SIM7600: {err}") from err
