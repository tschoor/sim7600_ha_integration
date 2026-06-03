"""Tests für SIM7600 Sensor-Entitäten."""

from unittest.mock import MagicMock

import pytest

from custom_components.sim7600.sensor import (
    SIM7600AltitudeSensor,
    SIM7600DateSensor,
    SIM7600NetworkModeSensor,
    SIM7600OperatorSensor,
    SIM7600SignalSensor,
    SIM7600SIMStatusSensor,
    SIM7600SpeedSensor,
    SIM7600SystemModeSensor,
    SIM7600TimeSensor,
)
from custom_components.sim7600.types import GpsData


@pytest.fixture
def gps_data() -> GpsData:
    """Beispiel-GPS-Daten."""
    return GpsData(
        latitude=52.524,
        longitude=13.409,
        altitude=50.0,
        speed=1.5,
        date="250321",
        time="023504.0",
    )


@pytest.fixture
def mock_coordinator(gps_data: GpsData) -> MagicMock:
    """Coordinator-Mock mit vollständigen Daten."""
    coordinator = MagicMock()
    coordinator.data = {
        "signal_dbm": -73,
        "operator": "Test Operator",
        "network_mode": "LTE",
        "system_mode": "Online",
        "sim_status": "READY",
        "gps": gps_data,
    }
    return coordinator


@pytest.fixture
def mock_entry() -> MagicMock:
    """Config-Entry-Mock."""
    entry = MagicMock()
    entry.entry_id = "test_entry"
    return entry


# --- Bestehende Tests ---


def test_sensors_native_value(
    mock_coordinator: MagicMock, mock_entry: MagicMock
) -> None:
    """Netzwerk-Sensoren liefern korrekte Werte."""
    signal_sensor = SIM7600SignalSensor(mock_coordinator, mock_entry)
    operator_sensor = SIM7600OperatorSensor(mock_coordinator, mock_entry)
    network_sensor = SIM7600NetworkModeSensor(mock_coordinator, mock_entry)
    system_sensor = SIM7600SystemModeSensor(mock_coordinator, mock_entry)

    assert signal_sensor.native_value == -73
    assert operator_sensor.native_value == "Test Operator"
    assert network_sensor.native_value == "LTE"
    assert system_sensor.native_value == "Online"


def test_sensors_unique_id(mock_coordinator: MagicMock, mock_entry: MagicMock) -> None:
    """Unique ID enthält Entry-ID und Klassenname."""
    signal_sensor = SIM7600SignalSensor(mock_coordinator, mock_entry)
    assert signal_sensor.unique_id == "test_entry_SIM7600SignalSensor"


# --- Neue Tests: SIM-Status ---


def test_sim_status_sensor_ready(
    mock_coordinator: MagicMock, mock_entry: MagicMock
) -> None:
    """SIM-Status-Sensor zeigt 'READY'."""
    sensor = SIM7600SIMStatusSensor(mock_coordinator, mock_entry)
    assert sensor.native_value == "READY"


def test_sim_status_sensor_none(
    mock_coordinator: MagicMock, mock_entry: MagicMock
) -> None:
    """SIM-Status-Sensor gibt None zurück wenn nicht verfügbar."""
    mock_coordinator.data = {"sim_status": None}
    sensor = SIM7600SIMStatusSensor(mock_coordinator, mock_entry)
    assert sensor.native_value is None


# --- Neue Tests: GPS-Sensoren ---


def test_speed_sensor_from_gps(
    mock_coordinator: MagicMock, mock_entry: MagicMock, gps_data: GpsData
) -> None:
    """Speed-Sensor liest Wert aus GpsData."""
    sensor = SIM7600SpeedSensor(mock_coordinator, mock_entry)
    assert sensor.native_value == gps_data.speed


def test_altitude_sensor_from_gps(
    mock_coordinator: MagicMock, mock_entry: MagicMock, gps_data: GpsData
) -> None:
    """Altitude-Sensor liest Wert aus GpsData."""
    sensor = SIM7600AltitudeSensor(mock_coordinator, mock_entry)
    assert sensor.native_value == gps_data.altitude


def test_date_sensor_from_gps(
    mock_coordinator: MagicMock, mock_entry: MagicMock, gps_data: GpsData
) -> None:
    """GNSS-Date-Sensor liest Wert aus GpsData."""
    sensor = SIM7600DateSensor(mock_coordinator, mock_entry)
    assert sensor.native_value == gps_data.date


def test_time_sensor_from_gps(
    mock_coordinator: MagicMock, mock_entry: MagicMock, gps_data: GpsData
) -> None:
    """GNSS-Time-Sensor liest Wert aus GpsData."""
    sensor = SIM7600TimeSensor(mock_coordinator, mock_entry)
    assert sensor.native_value == gps_data.time


def test_gps_sensors_return_none_when_no_gps(
    mock_coordinator: MagicMock, mock_entry: MagicMock
) -> None:
    """GPS-Sensoren geben None zurück wenn keine GPS-Daten vorhanden."""
    mock_coordinator.data = {"gps": None}
    speed = SIM7600SpeedSensor(mock_coordinator, mock_entry)
    altitude = SIM7600AltitudeSensor(mock_coordinator, mock_entry)
    date = SIM7600DateSensor(mock_coordinator, mock_entry)
    time = SIM7600TimeSensor(mock_coordinator, mock_entry)
    assert speed.native_value is None
    assert altitude.native_value is None
    assert date.native_value is None
    assert time.native_value is None
