"""Tests for the SIM7600 GPS parsing."""

from unittest.mock import patch

import pytest

from custom_components.sim7600.modem import SIM7600Modem


@pytest.mark.parametrize(
    "gps_line,expected",
    [
        (
            "+CGPSINFO: 3113.343286,N,12121.259046,E,250321,023504.0,45.0,0.0,0.0",
            {"latitude": 31.2223881, "longitude": 121.35431743333333, "altitude": 45.0},
        ),
        (
            "+CGPSINFO: 5231.450000,N,01324.550000,E,250321,023504.0,10.0,0.0,0.0",
            {
                "latitude": 52.524166666666666,
                "longitude": 13.409166666666667,
                "altitude": 10.0,
            },
        ),
        (
            "+CGPSINFO: ,,,,,,,,",
            None,
        ),
    ],
)
async def test_get_gps_info_parsing(gps_line, expected):
    """Test parsing of GPS info."""
    modem = SIM7600Modem("/dev/ttyUSB2", 115200)
    with patch.object(modem, "send_command", return_value=[gps_line]):
        info = await modem.get_gps_info()
        if expected is None:
            assert info is None
        else:
            assert info["latitude"] == pytest.approx(expected["latitude"])
            assert info["longitude"] == pytest.approx(expected["longitude"])
            assert info["altitude"] == expected["altitude"]
