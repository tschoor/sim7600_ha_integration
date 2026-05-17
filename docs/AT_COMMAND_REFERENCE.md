# SIM7600 AT Command Architecture

This document defines the interface for communicating with the SIM7600 module using AT commands.

## Communication Protocol
- **Termination:** All commands must be terminated with `
` (CRLF).
- **Asynchronicity:** All I/O must be non-blocking. Use `asyncio` streams.
- **Error Handling:** On `ERROR`, `+CME ERROR`, or `+CMS ERROR`, validate state via `AT+CPIN?` and `AT+CSQ`.

## Command Categories
1. **System & ID:** Initialized at startup (`AT+CGMI`, `AT+CGMM`, `AT+CGSN`, `AT+CSUB`, `AT+CGMR`).
2. **Network & Signal:** Polled at configurable frequency (`AT+CSQ`, `AT+CPSI?`, `AT+CREG?`, `AT+CGREG?`).
3. **GNSS:** Polled at configurable frequency (`AT+CGPSINFO`).
4. **SMS:** Event-driven/On-demand (`AT+CMGL="ALL"`, `AT+CMGR`, `AT+CMGS`).
5. **Telephony:** On-demand (`ATD`, `ATA`, `AT+CHUP`).

## Implementation Strategy
- **`SIM7600Modem` class:** Centralized command execution with `asyncio.Lock` to ensure serialized access to the serial port.
- **`SIM7600DataUpdateCoordinator`:** Manages the polling intervals and delegates data updates to the `SIM7600Modem`.
