"""Datentypen für die SIM7600 Integration."""

from dataclasses import dataclass


@dataclass
class GpsData:
    """GPS-Positionsdaten vom Modem (AT+CGPSINFO).

    Alle Felder sind verpflichtend. Fehlt ein Feld in der Modem-Antwort,
    wird None zurückgegeben statt eines partiell befüllten GpsData-Objekts.
    """

    latitude: float
    longitude: float
    altitude: float
    speed: float
    date: str
    time: str


@dataclass
class SmsData:
    """SMS-Nachricht vom Modem (AT+CMGL)."""

    index: int
    sender: str
    timestamp: str
    message: str
