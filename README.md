# SIM7600 4G & GPS Gateway Integration for Home Assistant

This custom integration allows you to connect a SIM7600 4G & GPS module to Home Assistant via a serial port (USB). It provides real-time monitoring of network status, signal strength, SMS capabilities, and GPS tracking.

## Features

*   **Network Monitoring**:
    *   Signal Strength (RSSI in dBm)
    *   Operator name
    *   Network Mode (LTE, GSM, etc.)
    *   System status
*   **Diagnostics**:
    *   IMEI number
    *   Firmware version
    *   SIM card status
*   **SMS Support**:
    *   Send SMS via `sim7600.send_sms` service
    *   Sensor for the last received SMS (with sender and timestamp attributes)
*   **GPS Tracking**:
    *   Integrated as a `device_tracker` entity (latitude, longitude, altitude)
*   **Setup**: 
    *   Easy UI configuration
    *   Support for automatic USB discovery

## Installation

### Via HACS (Recommended)
1. Open HACS in your Home Assistant.
2. Click the three dots (⋮) in the top right -> **Custom repositories**.
3. Add `https://github.com/tschoor/sim7600_ha_integration` as category **Integration**.
4. Search for "SIM7600 4G & GPS Gateway" and click **Download**.
5. Restart Home Assistant.

### Manual Installation
1. Copy the `custom_components/sim7600` directory to your `custom_components` folder in your Home Assistant configuration directory.
2. Restart Home Assistant.

## Configuration
1. Go to **Settings** -> **Devices & Services**.
2. Click **+ Add Integration**.
3. Search for **SIM7600 4G & GPS Gateway**.
4. Select the serial port (e.g., `/dev/ttyUSB2`) and baud rate.

## Services
*   `sim7600.send_sms`:
    *   `number`: Recipient's phone number.
    *   `message`: Message text.

---
*Built with ❤️ for Home Assistant.*
