"""Tests for the SIM7600 config flow."""

from unittest.mock import MagicMock, patch

import pytest
from homeassistant import config_entries, data_entry_flow
from homeassistant.components import usb

from custom_components.sim7600.const import CONF_BAUD_RATE, CONF_SERIAL_PORT, DOMAIN


@pytest.fixture(autouse=True)
def mock_serial_list():
    """Mock serial port list."""
    with patch("serial.tools.list_ports.comports") as mock:
        port = MagicMock()
        port.device = "/dev/ttyUSB2"
        port.description = "SIM7600 AT Port"
        mock.return_value = [port]
        yield mock


@pytest.fixture
def mock_serial():
    """Mock serial.Serial."""
    with patch("serial.Serial") as mock:
        yield mock


async def test_flow_init(hass):
    """Prüft, ob der Konfigurations-Dialog in HA startet."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )
    assert result["type"] == data_entry_flow.FlowResultType.FORM
    assert result["step_id"] == "user"


async def test_user_flow_success(hass, mock_serial):
    """Test successful user flow."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )

    result = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        {
            CONF_SERIAL_PORT: "/dev/ttyUSB2",
            CONF_BAUD_RATE: 115200,
        },
    )

    assert result["type"] == data_entry_flow.FlowResultType.CREATE_ENTRY
    assert result["title"] == "/dev/ttyUSB2"
    assert result["data"] == {
        CONF_SERIAL_PORT: "/dev/ttyUSB2",
        CONF_BAUD_RATE: 115200,
    }


async def test_user_flow_cannot_connect(hass, mock_serial):
    """Test user flow when connection fails."""
    mock_serial.side_effect = Exception("Connection failed")

    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )

    result = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        {
            CONF_SERIAL_PORT: "/dev/ttyUSB2",
            CONF_BAUD_RATE: 115200,
        },
    )

    assert result["type"] == data_entry_flow.FlowResultType.FORM
    assert result["errors"] == {"base": "cannot_connect"}


async def test_usb_discovery(hass):
    """Test USB discovery flow."""
    discovery_info = usb.UsbServiceInfo(
        device="/dev/ttyUSB2",
        vid="1E0E",
        pid="9001",
        serial_number="123456",
        manufacturer="SIMTech",
        description="SIM7600",
    )

    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USB}, data=discovery_info
    )

    assert result["type"] == data_entry_flow.FlowResultType.FORM
    assert result["step_id"] == "discovery_confirm"

    result = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        user_input={},
    )

    assert result["type"] == data_entry_flow.FlowResultType.CREATE_ENTRY
    assert result["title"] == "/dev/ttyUSB2"
    assert result["data"] == {
        CONF_SERIAL_PORT: "/dev/ttyUSB2",
        CONF_BAUD_RATE: 115200,
    }
