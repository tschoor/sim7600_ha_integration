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
    """Representation of a SIM7600 device tracker."""

    _attr_device_tracker_dict: dict[str, Any] = {}

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
    def latitude(self) -> float | None:
        """Return latitude value of the device."""
        gps = self.coordinator.data.get("gps")
        return gps.get("latitude") if gps else None

    @property
    def longitude(self) -> float | None:
        """Return longitude value of the device."""
        gps = self.coordinator.data.get("gps")
        return gps.get("longitude") if gps else None

    @property
    def altitude(self) -> float | None:
        """Return altitude value of the device."""
        gps = self.coordinator.data.get("gps")
        return gps.get("altitude") if gps else None

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return extra state attributes."""
        gps = self.coordinator.data.get("gps")
        if gps:
            return {
                "date": gps.get("date"),
                "time": gps.get("time"),
                "speed": gps.get("speed"),
                "altitude": gps.get("altitude"),
            }
        return {}
