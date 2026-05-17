"""Tests for the SIM7600 coordinator."""
from unittest.mock import AsyncMock, patch
import pytest
from homeassistant.helpers.update_coordinator import UpdateFailed
from custom_components.sim7600.coordinator import SIM7600DataUpdateCoordinator

@pytest.fixture
def mock_modem():
    """Mock the SIM7600 modem."""
    modem = AsyncMock()
    modem.get_signal_quality.return_value = 20
    modem.get_operator.return_value = "Test Operator"
    modem.get_network_info.return_value = {
        "mode": "LTE",
        "system_mode": "Online",
    }
    modem.get_imei.return_value = "123456789012345"
    modem.get_firmware.return_value = "V1.0"
    modem.get_sim_status.return_value = "READY"
    return modem

async def test_coordinator_update_success(hass, mock_modem):
    """Test successful coordinator update."""
    coordinator = SIM7600DataUpdateCoordinator(hass, mock_modem)
    data = await coordinator._async_update_data()

    assert data["rssi"] == 20
    assert data["signal_dbm"] == -73  # -113 + (20 * 2)
    assert data["operator"] == "Test Operator"
    assert data["network_mode"] == "LTE"
    assert data["system_mode"] == "Online"
    assert data["imei"] == "123456789012345"
    assert data["firmware"] == "V1.0"
    assert data["sim_status"] == "READY"

async def test_coordinator_update_failed(hass, mock_modem):
    """Test coordinator update failure."""
    mock_modem.get_signal_quality.side_effect = Exception("Connection error")
    coordinator = SIM7600DataUpdateCoordinator(hass, mock_modem)

    with pytest.raises(UpdateFailed):
        await coordinator._async_update_data()
