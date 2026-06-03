"""Support for SIM7600 sensors."""

from __future__ import annotations

from typing import Any

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    SIGNAL_STRENGTH_DECIBELS_MILLIWATT,
    UnitOfLength,
    UnitOfSpeed,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import EntityCategory
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import SIM7600DataUpdateCoordinator
from .types import GpsData, SmsData


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up SIM7600 sensors based on a config entry."""
    coordinator = hass.data[DOMAIN][entry.entry_id]["coordinator"]

    async_add_entities(
        [
            SIM7600SignalSensor(coordinator, entry),
            SIM7600OperatorSensor(coordinator, entry),
            SIM7600NetworkModeSensor(coordinator, entry),
            SIM7600SystemModeSensor(coordinator, entry),
            SIM7600IMEISensor(coordinator, entry),
            SIM7600FirmwareSensor(coordinator, entry),
            SIM7600SIMStatusSensor(coordinator, entry),
            SIM7600LastSMSSensor(coordinator, entry),
            SIM7600SpeedSensor(coordinator, entry),
            SIM7600AltitudeSensor(coordinator, entry),
            SIM7600DateSensor(coordinator, entry),
            SIM7600TimeSensor(coordinator, entry),
        ]
    )


class SIM7600SensorBase(CoordinatorEntity[SIM7600DataUpdateCoordinator], SensorEntity):
    """Base class for SIM7600 sensors."""

    def __init__(
        self, coordinator: SIM7600DataUpdateCoordinator, entry: ConfigEntry
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{entry.entry_id}_{self.__class__.__name__}"
        self._attr_device_info = {
            "identifiers": {(DOMAIN, entry.entry_id)},
            "name": "SIM7600 Modem",
            "manufacturer": "SimTech",
            "model": "SIM7600 Series",
        }


class SIM7600SignalSensor(SIM7600SensorBase):
    """Representation of a SIM7600 signal strength sensor."""

    _attr_name = "Signal Strength"
    _attr_device_class = SensorDeviceClass.SIGNAL_STRENGTH
    _attr_native_unit_of_measurement = SIGNAL_STRENGTH_DECIBELS_MILLIWATT
    _attr_state_class = SensorStateClass.MEASUREMENT

    @property
    def native_value(self) -> float | None:
        """Return the state of the sensor."""
        return self.coordinator.data.get("signal_dbm")


class SIM7600OperatorSensor(SIM7600SensorBase):
    """Representation of a SIM7600 operator sensor."""

    _attr_name = "Operator"
    _attr_icon = "mdi:antenna"

    @property
    def native_value(self) -> str | None:
        """Return the state of the sensor."""
        return self.coordinator.data.get("operator")


class SIM7600NetworkModeSensor(SIM7600SensorBase):
    """Representation of a SIM7600 network mode sensor."""

    _attr_name = "Network Mode"
    _attr_icon = "mdi:cellular-4g"

    @property
    def native_value(self) -> str | None:
        """Return the state of the sensor."""
        return self.coordinator.data.get("network_mode")


class SIM7600SystemModeSensor(SIM7600SensorBase):
    """Representation of a SIM7600 system mode sensor."""

    _attr_name = "System Mode"
    _attr_icon = "mdi:cog"

    @property
    def native_value(self) -> str | None:
        """Return the state of the sensor."""
        return self.coordinator.data.get("system_mode")


class SIM7600IMEISensor(SIM7600SensorBase):
    """Representation of a SIM7600 IMEI sensor."""

    _attr_name = "IMEI"
    _attr_icon = "mdi:barcode"
    _attr_entity_category: EntityCategory = EntityCategory.DIAGNOSTIC

    @property
    def native_value(self) -> str | None:
        """Return the state of the sensor."""
        return self.coordinator.data.get("imei")


class SIM7600FirmwareSensor(SIM7600SensorBase):
    """Representation of a SIM7600 firmware sensor."""

    _attr_name = "Firmware Version"
    _attr_icon = "mdi:software-control-major-weight"
    _attr_entity_category: EntityCategory = EntityCategory.DIAGNOSTIC

    @property
    def native_value(self) -> str | None:
        """Return the state of the sensor."""
        return self.coordinator.data.get("firmware")


class SIM7600SIMStatusSensor(SIM7600SensorBase):
    """Representation of a SIM7600 SIM status sensor."""

    _attr_name = "SIM Status"
    _attr_icon = "mdi:sim"
    _attr_entity_category: EntityCategory = EntityCategory.DIAGNOSTIC

    @property
    def native_value(self) -> str | None:
        """Return the state of the sensor."""
        return self.coordinator.data.get("sim_status")


class SIM7600LastSMSSensor(SIM7600SensorBase):
    """Representation of a SIM7600 last SMS sensor."""

    _attr_name = "Last SMS"
    _attr_icon = "mdi:message-text"

    @property
    def native_value(self) -> str | None:
        """Return the state of the sensor."""
        last_sms: SmsData | None = self.coordinator.data.get("last_sms")
        if last_sms is not None:
            return last_sms.message
        return None

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return extra state attributes."""
        last_sms: SmsData | None = self.coordinator.data.get("last_sms")
        if last_sms is not None:
            return {
                "sender": last_sms.sender,
                "timestamp": last_sms.timestamp,
            }
        return {}


class SIM7600SpeedSensor(SIM7600SensorBase):
    """Representation of a SIM7600 speed sensor."""

    _attr_name = "Speed"
    _attr_device_class = SensorDeviceClass.SPEED
    _attr_native_unit_of_measurement = UnitOfSpeed.KILOMETERS_PER_HOUR
    _attr_state_class = SensorStateClass.MEASUREMENT

    @property
    def native_value(self) -> float | None:
        """Return the state of the sensor."""
        gps: GpsData | None = self.coordinator.data.get("gps")
        return gps.speed if gps is not None else None


class SIM7600AltitudeSensor(SIM7600SensorBase):
    """Representation of a SIM7600 altitude sensor."""

    _attr_name = "Altitude"
    _attr_device_class = SensorDeviceClass.DISTANCE
    _attr_native_unit_of_measurement = UnitOfLength.METERS
    _attr_state_class = SensorStateClass.MEASUREMENT

    @property
    def native_value(self) -> float | None:
        """Return the state of the sensor."""
        gps: GpsData | None = self.coordinator.data.get("gps")
        return gps.altitude if gps is not None else None


class SIM7600DateSensor(SIM7600SensorBase):
    """Representation of a SIM7600 GNSS date sensor."""

    _attr_name = "GNSS Date"

    @property
    def native_value(self) -> str | None:
        """Return the state of the sensor."""
        gps: GpsData | None = self.coordinator.data.get("gps")
        return gps.date if gps is not None else None


class SIM7600TimeSensor(SIM7600SensorBase):
    """Representation of a SIM7600 GNSS time sensor."""

    _attr_name = "GNSS Time"

    @property
    def native_value(self) -> str | None:
        """Return the state of the sensor."""
        gps: GpsData | None = self.coordinator.data.get("gps")
        return gps.time if gps is not None else None
