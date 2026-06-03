"""Tests für GPS-Parsing im SIM7600 Modem."""

from unittest.mock import patch

import pytest

from custom_components.sim7600.modem import SIM7600Modem
from custom_components.sim7600.types import GpsData


@pytest.mark.parametrize(
    "gps_line,expected_lat,expected_lon,expected_alt",
    [
        (
            "+CGPSINFO: 3113.343286,N,12121.259046,E,250321,023504.0,45.0,0.0,0.0",
            31.2223881,
            121.35431743333333,
            45.0,
        ),
        (
            "+CGPSINFO: 5231.450000,N,01324.550000,E,250321,023504.0,10.0,0.0,0.0",
            52.524166666666666,
            13.409166666666667,
            10.0,
        ),
    ],
)
async def test_get_gps_info_parsing(
    gps_line: str, expected_lat: float, expected_lon: float, expected_alt: float
) -> None:
    """Korrekte GPS-Koordinatenumrechnung aus AT+CGPSINFO."""
    modem = SIM7600Modem("/dev/ttyUSB2", 115200)
    with patch.object(modem, "send_command", return_value=[gps_line]):
        info = await modem.get_gps_info()
    assert isinstance(info, GpsData)
    assert info.latitude == pytest.approx(expected_lat)
    assert info.longitude == pytest.approx(expected_lon)
    assert info.altitude == expected_alt


async def test_get_gps_info_empty_response() -> None:
    """Leere GPS-Antwort → None."""
    modem = SIM7600Modem("/dev/ttyUSB2", 115200)
    with patch.object(modem, "send_command", return_value=["+CGPSINFO: ,,,,,,,,"]):
        info = await modem.get_gps_info()
    assert info is None


async def test_all_fields_mandatory_speed_missing() -> None:
    """Fehlende Geschwindigkeit → None (Pflichtfeld)."""
    modem = SIM7600Modem("/dev/ttyUSB2", 115200)
    line = "+CGPSINFO: 5231.450000,N,01324.550000,E,250321,023504.0,10.0,,0.0"
    with patch.object(modem, "send_command", return_value=[line]):
        info = await modem.get_gps_info()
    assert info is None


async def test_all_fields_mandatory_altitude_missing() -> None:
    """Fehlende Höhe → None (Pflichtfeld)."""
    modem = SIM7600Modem("/dev/ttyUSB2", 115200)
    line = "+CGPSINFO: 5231.450000,N,01324.550000,E,250321,023504.0,,0.0,0.0"
    with patch.object(modem, "send_command", return_value=[line]):
        info = await modem.get_gps_info()
    assert info is None


async def test_coordinates_southwest() -> None:
    """Süd/West-Koordinaten haben negative Vorzeichen."""
    modem = SIM7600Modem("/dev/ttyUSB2", 115200)
    line = "+CGPSINFO: 3113.343286,S,12121.259046,W,250321,023504.0,45.0,0.0,0.0"
    with patch.object(modem, "send_command", return_value=[line]):
        info = await modem.get_gps_info()
    assert info is not None
    assert info.latitude < 0
    assert info.longitude < 0
    assert info.latitude == pytest.approx(-31.2223881)
    assert info.longitude == pytest.approx(-121.35431743333333)
