"""Konstanten für die SIM7600 Integration."""

from logging import Logger, getLogger

LOGGER: Logger = getLogger(__package__)

DOMAIN = "sim7600"
CONF_SERIAL_PORT = "serial_port"
CONF_BAUD_RATE = "baud_rate"
CONF_POLLING_INTERVAL = "polling_interval"
CONF_GNSS_INTERVAL = "gnss_interval"
CONF_DEBUG_MODE = "debug_mode"

DEFAULT_BAUD = 115200
DEFAULT_POLLING_INTERVAL = 60  # seconds
DEFAULT_GNSS_INTERVAL = 300  # seconds
