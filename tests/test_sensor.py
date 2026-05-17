"""Tests for the SIM7600 sensors."""
from unittest.mock import MagicMock, patch
import pytest
from homeassistant.core import HomeAssistant
from custom_components.sim7600.const import DOMAIN
from custom_components.sim7600.sensor import (
    SIM7600SignalSensor,
    SIM7600OperatorSensor,
    SIM7600NetworkModeSensor,
    SIM7600SystemModeSensor,
)

@pytest.fixture
def mock_coordinator():
    """Mock the SIM7600 coordinator."""
    coordinator = MagicMock()
    coordinator.data = {
        "signal_dbm": -73,
        "operator": "Test Operator",
        "network_mode": "LTE",
        "system_mode": "Online",
    }
    return coordinator

@pytest.fixture
def mock_entry():
    """Mock a config entry."""
    entry = MagicMock()
    entry.entry_id = "test_entry"
    return entry

def test_sensors_native_value(mock_coordinator, mock_entry):
    """Test the native value of sensors."""
    signal_sensor = SIM7600SignalSensor(mock_coordinator, mock_entry)
    operator_sensor = SIM7600OperatorSensor(mock_coordinator, mock_entry)
    network_sensor = SIM7600NetworkModeSensor(mock_coordinator, mock_entry)
    system_sensor = SIM7600SystemModeSensor(mock_coordinator, mock_entry)

    assert signal_sensor.native_value == -73
    assert operator_sensor.native_value == "Test Operator"
    assert network_sensor.native_value == "LTE"
    assert system_sensor.native_value == "Online"

def test_sensors_unique_id(mock_coordinator, mock_entry):
    """Test the unique ID of sensors."""
    signal_sensor = SIM7600SignalSensor(mock_coordinator, mock_entry)
    assert signal_sensor.unique_id == "test_entry_SIM7600SignalSensor"
