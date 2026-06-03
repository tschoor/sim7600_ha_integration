"""Tests für den SIM7600 Coordinator."""

import logging
from unittest.mock import AsyncMock, MagicMock

import pytest
from homeassistant.helpers.update_coordinator import UpdateFailed

from custom_components.sim7600.const import CONF_GNSS_INTERVAL, CONF_POLLING_INTERVAL
from custom_components.sim7600.coordinator import SIM7600DataUpdateCoordinator
from custom_components.sim7600.types import GpsData, SmsData


@pytest.fixture
def mock_entry() -> MagicMock:
    """Config-Entry-Mock."""
    entry = MagicMock()
    entry.data = {
        CONF_POLLING_INTERVAL: 60,
        CONF_GNSS_INTERVAL: 300,
    }
    entry.options = {}
    return entry


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
def mock_modem(gps_data: GpsData) -> AsyncMock:
    """Modem-Mock mit typischen Antworten."""
    modem = AsyncMock()
    modem.port = "/dev/ttyUSB2"
    modem.baudrate = 115200
    modem.get_signal_quality.return_value = 20
    modem.get_operator.return_value = "Test Operator"
    modem.get_network_info.return_value = {
        "mode": "LTE",
        "system_mode": "Online",
    }
    modem.get_imei.return_value = "123456789012345"
    modem.get_firmware.return_value = "V1.0"
    modem.get_manufacturer.return_value = "SimTech"
    modem.get_model.return_value = "SIM7600E-H"
    modem.get_registration_status.return_value = 1
    modem.get_gprs_registration_status.return_value = 1
    modem.get_sim_status.return_value = "READY"
    modem.get_unread_sms.return_value = []
    modem.set_gps.return_value = True
    modem.get_gps_info.return_value = gps_data
    modem.delete_sms.return_value = True
    return modem


# --- Bestehende Tests ---


async def test_coordinator_update_success(
    hass: object, mock_modem: AsyncMock, mock_entry: MagicMock
) -> None:
    """Erfolgreicher Update-Zyklus liefert vollständige Daten."""
    coordinator = SIM7600DataUpdateCoordinator(hass, mock_modem, mock_entry)  # type: ignore[arg-type]
    data = await coordinator._async_update_data()

    assert data["rssi"] == 20
    assert data["signal_dbm"] == -73  # -113 + (20 * 2)
    assert data["operator"] == "Test Operator"
    assert data["network_mode"] == "LTE"
    assert data["system_mode"] == "Online"
    assert data["imei"] == "123456789012345"
    assert data["firmware"] == "V1.0"
    assert data["manufacturer"] == "SimTech"
    assert data["model"] == "SIM7600E-H"


async def test_coordinator_update_failed(
    hass: object, mock_modem: AsyncMock, mock_entry: MagicMock
) -> None:
    """Exception in Verbindungsschicht → UpdateFailed."""
    mock_modem.get_signal_quality.side_effect = Exception("Connection error")
    coordinator = SIM7600DataUpdateCoordinator(hass, mock_modem, mock_entry)  # type: ignore[arg-type]

    with pytest.raises(UpdateFailed):
        await coordinator._async_update_data()


# --- Neue Tests: SIM-Status ---


async def test_sim_status_in_coordinator_data(
    hass: object, mock_modem: AsyncMock, mock_entry: MagicMock
) -> None:
    """sim_status wird im Coordinator-Datenobjekt befüllt."""
    coordinator = SIM7600DataUpdateCoordinator(hass, mock_modem, mock_entry)  # type: ignore[arg-type]
    data = await coordinator._async_update_data()
    assert data["sim_status"] == "READY"


# --- Neue Tests: State-Persistenz ---


async def test_state_persistence_gps_on_none_response(
    hass: object, mock_modem: AsyncMock, mock_entry: MagicMock, gps_data: GpsData
) -> None:
    """GPS gibt None zurück → letzter bekannter GPS-Fix bleibt im data-Dict."""
    coordinator = SIM7600DataUpdateCoordinator(hass, mock_modem, mock_entry)  # type: ignore[arg-type]
    coordinator.last_gnss_update = 0.0  # Interval abgelaufen
    # Erster Aufruf: GPS-Daten vorhanden
    await coordinator._async_update_data()
    # Zweiter Aufruf: GPS gibt None zurück
    mock_modem.get_gps_info.return_value = None
    coordinator.last_gnss_update = 0.0
    data = await coordinator._async_update_data()
    # Letzter Fix muss erhalten bleiben
    assert data["gps"] is not None
    assert data["gps"].latitude == gps_data.latitude


async def test_state_persistence_signal_on_none_response(
    hass: object, mock_modem: AsyncMock, mock_entry: MagicMock
) -> None:
    """Signal gibt None zurück → letzter bekannter dBm-Wert bleibt."""
    coordinator = SIM7600DataUpdateCoordinator(hass, mock_modem, mock_entry)  # type: ignore[arg-type]
    # Erster Aufruf: Signal vorhanden
    await coordinator._async_update_data()
    # Zweiter Aufruf: Signal nicht verfügbar
    mock_modem.get_signal_quality.return_value = None
    data = await coordinator._async_update_data()
    assert data["signal_dbm"] == -73  # Letzter bekannter Wert


async def test_no_update_failed_on_partial_error(
    hass: object, mock_modem: AsyncMock, mock_entry: MagicMock
) -> None:
    """Einzelner AT-Befehl gibt None zurück → kein UpdateFailed."""
    mock_modem.get_operator.return_value = None
    coordinator = SIM7600DataUpdateCoordinator(hass, mock_modem, mock_entry)  # type: ignore[arg-type]
    # Kein Exception erwartet
    data = await coordinator._async_update_data()
    assert data is not None


# --- Neue Tests: SMS-Löschung ---


async def test_sms_deleted_after_reading(
    hass: object, mock_modem: AsyncMock, mock_entry: MagicMock
) -> None:
    """Nach dem Lesen einer SMS wird delete_sms mit korrektem Index aufgerufen."""
    sms = SmsData(
        index=3, sender="+49123", timestamp="21/03/25,10:00:00+00", message="Test"
    )
    mock_modem.get_unread_sms.return_value = [sms]
    coordinator = SIM7600DataUpdateCoordinator(hass, mock_modem, mock_entry)  # type: ignore[arg-type]
    await coordinator._async_update_data()
    mock_modem.delete_sms.assert_called_once_with(3)


async def test_sms_last_sms_updated(
    hass: object, mock_modem: AsyncMock, mock_entry: MagicMock
) -> None:
    """Neue SMS wird als last_sms gespeichert."""
    sms = SmsData(
        index=1, sender="+111", timestamp="21/03/25,10:00:00+00", message="Hallo"
    )
    mock_modem.get_unread_sms.return_value = [sms]
    coordinator = SIM7600DataUpdateCoordinator(hass, mock_modem, mock_entry)  # type: ignore[arg-type]
    data = await coordinator._async_update_data()
    assert data["last_sms"] is not None
    assert data["last_sms"].message == "Hallo"


# --- Neue Tests: GPS-Timing ---


async def test_gps_not_fetched_before_interval(
    hass: object, mock_modem: AsyncMock, mock_entry: MagicMock
) -> None:
    """GPS wird nicht abgerufen, wenn das Interval noch nicht abgelaufen ist."""
    import time

    coordinator = SIM7600DataUpdateCoordinator(hass, mock_modem, mock_entry)  # type: ignore[arg-type]
    coordinator.gps_enabled = True
    coordinator.last_gnss_update = time.time()  # Gerade abgerufen
    await coordinator._async_update_data()
    mock_modem.get_gps_info.assert_not_called()


async def test_gps_fetched_after_interval(
    hass: object, mock_modem: AsyncMock, mock_entry: MagicMock
) -> None:
    """GPS wird abgerufen wenn das Interval abgelaufen ist."""
    coordinator = SIM7600DataUpdateCoordinator(hass, mock_modem, mock_entry)  # type: ignore[arg-type]
    coordinator.gps_enabled = True
    coordinator.last_gnss_update = 0.0  # Sehr lange her
    await coordinator._async_update_data()
    mock_modem.get_gps_info.assert_called_once()


# --- Neue Tests: GPS-Aktivierungs-Retry ---


async def test_gps_activation_retried_when_false(
    hass: object, mock_modem: AsyncMock, mock_entry: MagicMock
) -> None:
    """Wenn set_gps() False zurückgibt, wird es im nächsten Zyklus erneut versucht."""
    mock_modem.set_gps.return_value = False
    coordinator = SIM7600DataUpdateCoordinator(hass, mock_modem, mock_entry)  # type: ignore[arg-type]
    await coordinator._async_update_data()
    assert not coordinator.gps_enabled
    # Zweiter Zyklus: erneuter Versuch
    await coordinator._async_update_data()
    assert mock_modem.set_gps.call_count == 2


# --- Neue Tests: Konsekutive Fehler-Warnung (Spec 6.5) ---


async def test_consecutive_failures_tracked(
    hass: object, mock_modem: AsyncMock, mock_entry: MagicMock
) -> None:
    """Aufeinanderfolgende UpdateFailed werden gezählt."""
    mock_modem.get_signal_quality.side_effect = Exception("Connection error")
    coordinator = SIM7600DataUpdateCoordinator(hass, mock_modem, mock_entry)  # type: ignore[arg-type]

    for _ in range(3):
        with pytest.raises(UpdateFailed):
            await coordinator._async_update_data()

    assert coordinator._consecutive_failures == 3


async def test_consecutive_failures_log_warning(
    hass: object,
    mock_modem: AsyncMock,
    mock_entry: MagicMock,
    caplog: pytest.LogCaptureFixture,
) -> None:
    """Mehr als 3 aufeinanderfolgende UpdateFailed → WARNING im Log."""
    mock_modem.get_signal_quality.side_effect = Exception("Connection error")
    coordinator = SIM7600DataUpdateCoordinator(hass, mock_modem, mock_entry)  # type: ignore[arg-type]

    with caplog.at_level(logging.WARNING, logger="custom_components.sim7600"):
        for _ in range(4):
            with pytest.raises(UpdateFailed):
                await coordinator._async_update_data()

    assert coordinator._consecutive_failures == 4
    assert any("WARNING" in r.levelname for r in caplog.records)


async def test_consecutive_failures_reset_on_success(
    hass: object, mock_modem: AsyncMock, mock_entry: MagicMock
) -> None:
    """Erfolgreicher Update setzt Fehler-Zähler zurück."""
    mock_modem.get_signal_quality.side_effect = [
        Exception("err"),
        Exception("err"),
        20,
    ]
    coordinator = SIM7600DataUpdateCoordinator(hass, mock_modem, mock_entry)  # type: ignore[arg-type]

    for _ in range(2):
        with pytest.raises(UpdateFailed):
            await coordinator._async_update_data()

    await coordinator._async_update_data()
    assert coordinator._consecutive_failures == 0


# --- Neue Tests: Statische Daten (Caching) ---


async def test_static_data_cached_after_first_call(
    hass: object, mock_modem: AsyncMock, mock_entry: MagicMock
) -> None:
    """IMEI/Firmware werden nur beim ersten Aufruf abgerufen."""
    coordinator = SIM7600DataUpdateCoordinator(hass, mock_modem, mock_entry)  # type: ignore[arg-type]
    await coordinator._async_update_data()
    await coordinator._async_update_data()
    # Nur einmal aufgerufen, nicht zweimal
    mock_modem.get_imei.assert_called_once()
    mock_modem.get_firmware.assert_called_once()
