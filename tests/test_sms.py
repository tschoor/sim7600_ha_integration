"""Tests for the SIM7600 SMS parsing."""
import pytest
from custom_components.sim7600.modem import SIM7600Modem
from unittest.mock import AsyncMock, patch

async def test_get_unread_sms_parsing():
    """Test parsing of unread SMS."""
    modem = SIM7600Modem("/dev/ttyUSB2", 115200)
    mock_responses = [
        'OK', # CMGF
        [
            '+CMGL: 1,"REC UNREAD","+1234567890",,"21/03/25,02:35:04+00"',
            'Hello from SIM7600!',
            'OK'
        ]
    ]
    
    with patch.object(modem, "send_command", side_effect=mock_responses):
        messages = await modem.get_unread_sms()
        assert len(messages) == 1
        assert messages[0]["sender"] == "+1234567890"
        assert messages[0]["message"] == "Hello from SIM7600!"
        assert messages[0]["timestamp"] == "21/03/25,02:35:04+00"
