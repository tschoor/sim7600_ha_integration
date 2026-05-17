"""Support for SIM7600 device tracker."""

from __future__ import annotations

from homeassistant.components.device_tracker import SourceType, TrackerEntity
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
        self._attr_device_tracker_dict = {}

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
    def source_type(self) -> SourceType:
        """Return the source type, eg gps or router, of the device."""
        return SourceType.GPS
