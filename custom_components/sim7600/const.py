"""Konstanten für die SIM7600 Integration."""
from logging import Logger, getLogger

LOGGER: Logger = getLogger(__package__)

DOMAIN = "sim7600"
CONF_SERIAL_PORT = "serial_port"
CONF_BAUD_RATE = "baud_rate"

DEFAULT_BAUD = 115200
