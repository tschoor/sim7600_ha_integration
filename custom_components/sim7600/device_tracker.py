"""Support for SIM7600 device tracker."""

from __future__ import annotations

from typing import Any

from homeassistant.components.device_tracker import TrackerEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import SIM7600DataUpdateCoordinator
from .types import GpsData


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up SIM7600 device tracker based on a config entry."""
    coordinator = hass.data[DOMAIN][entry.entry_id]["coordinator"]
    async_add_entities([SIM7600DeviceTracker(coordinator, entry)])


class SIM7600DeviceTracker(
    CoordinatorEntity[SIM7600DataUpdateCoordinator], TrackerEntity
):
    """Representation of a SIM7600 device tracker.

    State-Persistenz: Der Coordinator cached den letzten bekannten GPS-Fix.
    Diese Entität zeigt immer den aktuellen Coordinator-Cache — nie unknown
    solange mindestens ein erfolgreicher Fix vorlag.
    """

    def __init__(
        self, coordinator: SIM7600DataUpdateCoordinator, entry: ConfigEntry
    ) -> None:
        """Initialize the tracker."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{entry.entry_id}_GPS"
        self._attr_name = "SIM7600 Modem"
        self._attr_device_info = {
            "identifiers": {(DOMAIN, entry.entry_id)},
            "name": "SIM7600 Modem",
            "manufacturer": "SimTech",
            "model": "SIM7600 Series",
        }

    @property
    def _gps(self) -> GpsData | None:
        """Aktueller GPS-Fix aus dem Coordinator-Cache."""
        return self.coordinator.data.get("gps")

    @property
    def latitude(self) -> float | None:
        """Return latitude value of the device."""
        gps = self._gps
        return gps.latitude if gps is not None else None

    @property
    def longitude(self) -> float | None:
        """Return longitude value of the device."""
        gps = self._gps
        return gps.longitude if gps is not None else None

    @property
    def altitude(self) -> float | None:
        """Return altitude value of the device."""
        gps = self._gps
        return gps.altitude if gps is not None else None

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return extra state attributes."""
        gps = self._gps
        if gps is not None:
            return {
                "date": gps.date,
                "time": gps.time,
                "speed": gps.speed,
                "altitude": gps.altitude,
            }
        return {}
