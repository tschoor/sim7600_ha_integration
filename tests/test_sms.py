"""Tests für SMS-Parsing im SIM7600 Modem."""

from unittest.mock import patch

from custom_components.sim7600.modem import SIM7600Modem
from custom_components.sim7600.types import SmsData


async def test_get_unread_sms_parsing() -> None:
    """Korrekte Extraktion aller SMS-Felder aus AT+CMGL-Antwort."""
    modem = SIM7600Modem("/dev/ttyUSB2", 115200)
    mock_responses = [
        ["OK"],
        [
            '+CMGL: 1,"REC UNREAD","+1234567890",,"21/03/25,02:35:04+00"',
            "Hello from SIM7600!",
            "OK",
        ],
    ]

    with patch.object(modem, "send_command", side_effect=mock_responses):
        messages = await modem.get_unread_sms()
    assert len(messages) == 1
    assert isinstance(messages[0], SmsData)
    assert messages[0].sender == "+1234567890"
    assert messages[0].message == "Hello from SIM7600!"
    assert messages[0].timestamp == "21/03/25,02:35:04+00"


async def test_sms_index_extracted() -> None:
    """SMS-Index wird korrekt aus der +CMGL-Zeile extrahiert."""
    modem = SIM7600Modem("/dev/ttyUSB2", 115200)
    mock_responses = [
        ["OK"],
        [
            '+CMGL: 7,"REC UNREAD","+1234567890",,"21/03/25,02:35:04+00"',
            "Test",
            "OK",
        ],
    ]

    with patch.object(modem, "send_command", side_effect=mock_responses):
        messages = await modem.get_unread_sms()
    assert len(messages) == 1
    assert messages[0].index == 7


async def test_multiple_sms_all_indices() -> None:
    """Alle Indizes werden korrekt aus mehreren +CMGL-Zeilen extrahiert."""
    modem = SIM7600Modem("/dev/ttyUSB2", 115200)
    mock_responses = [
        ["OK"],
        [
            '+CMGL: 2,"REC UNREAD","+111",,"21/03/25,01:00:00+00"',
            "First",
            '+CMGL: 9,"REC UNREAD","+222",,"21/03/25,02:00:00+00"',
            "Second",
            "OK",
        ],
    ]

    with patch.object(modem, "send_command", side_effect=mock_responses):
        messages = await modem.get_unread_sms()
    assert len(messages) == 2
    assert messages[0].index == 2
    assert messages[1].index == 9
