# GEMINI_RULES.md: SIM7600 Integration Standards

## 🎯 Vision
Entwicklung einer offiziellen, stabilen und asynchronen Home Assistant Integration für das SIM7600X Modul, die den strengen **Home Assistant Core Quality Standards** entspricht.

---

## 🛠 1. Coding Standards (Non-Negotiable)
* **Asynchronität:** Absolutes Verbot von blockierenden I/O-Aufrufen im Haupt-Thread (`time.sleep()`, `serial.read()`, `requests.get()`). 
    * Nutze `pyserial-asyncio` oder `hass.async_add_executor_job` für die Kommunikation mit der Hardware.
* **Typisierung:** Strikte Verwendung von **Python Type Hints**. Jede Funktion muss vollständig typisiert sein. Ziel: `mypy --strict` Konformität.
* **Formatierung:** Der Code muss den Regeln von `ruff` entsprechen. Bevorzuge klare, selbsterklärende Variablennamen gegenüber kurzen Kürzeln.
* **Dokumentation:** Jede öffentliche Methode benötigt einen Docstring nach **PEP 257**.

---

## 🏗 2. Home Assistant Architektur
* **DataUpdateCoordinator:** Alle Sensor-Daten werden über einen zentralen `DataUpdateCoordinator` abgerufen. Kein individuelles Polling in den Sensor-Entitäten.
* **Config Flow:** Die Einrichtung erfolgt ausschließlich über die Benutzeroberfläche (`config_flow.py`). Keine YAML-Konfiguration für Endnutzer.
* **Entitäten:** Nutze dedizierte Plattformen (`sensor.py`, `device_tracker.py`, `button.py`). Jede Entität muss eine `unique_id` besitzen.
* **Internationalisierung:** Hardcodierte Strings sind verboten. Nutze `strings.json` und `translations/*.json`.

---

## 🛰 3. Hardware-Spezifika (SIM7600)
* **Schnittstelle:** UART (Standard: `/dev/ttyS0`), Baudrate: `115200`.
* **Power Management:** GPIO 6 triggert den Power-Key. Implementiere Logik, um zu prüfen, ob das Modul bereits wach ist, bevor der Key getriggert wird.
* **AT-Befehle:** Befehle müssen effizient verkettet werden. Wartezeiten zwischen Befehlen müssen asynchron gehandhabt werden.

---

## 🔄 4. Workflow & Qualitätssicherung
* **Lokale CI-Parität:** Vor jedem Push müssen alle CI-Schritte (Ruff, Mypy, Safety, Pytest) lokal erfolgreich ausgeführt werden. Ein Push ohne lokale Verifizierung ist untersagt.
* **Commit-Disziplin:** Jede Commit-Nachricht muss auf einer Analyse des `git diff` basieren und den logischen Kern der Änderung präzise beschreiben.
* **Logging Standards:**
  * `TRACE`: Rohdaten vom seriellen Port (nur bei aktiviertem Debug-Modus).
  * `DEBUG`: Senden/Empfangen von AT-Befehlen.
  * `INFO`: Wichtige Zustandsänderungen der Integration.
  * `ERROR`: Fehler bei Verbindungen, Timeout oder Parsing.
* **CI Ownership:** Ein Task gilt erst dann als "Done", wenn sowohl der lokale Lauf als auch die GitHub Actions Pipeline erfolgreich ("grün") sind.
* **Autonomes Troubleshooting:** Bei Pipeline-Fehlern muss der Agent eigenständig die Logs analysieren und eine Korrekturstrategie im Plan-Modus entwickeln.

---

## 🤖 5. Anweisungen für die KI (System Prompt)
1. **Analysiere** immer zuerst die bestehende Struktur und den aktuellen `git diff`, bevor du Code generierst oder einen Commit durchführst.
2. **Verweigere** Implementierungen, die gegen die Asynchronität von Home Assistant verstoßen oder die lokale CI-Parität gefährden.
3. **Handle proaktiv:** Führe die gesamte Test- und Linting-Suite lokal aus, bevor du die Arbeit als abgeschlossen meldest.
4. **Präzision:** Erstelle logische Commit-Nachrichten, die den "Warum"-Aspekt der Änderung basierend auf dem tatsächlichen Diff hervorheben.
