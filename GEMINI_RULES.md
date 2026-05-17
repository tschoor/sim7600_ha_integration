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
* **Statische Analyse:** Führe vor jeder Code-Änderung eine Analyse via `ruff check .` und `mypy .` durch.
* **Testing:** Für jede neue Logik (insb. Parser) muss ein Testfall in `tests/` existieren. Nutze `pytest` und Mocks für die Hardware-Antworten.
* **Dokumentation:** Halte die **arc42**-Dokumente (`docs/arc42/*.md`) synchron zum Code. Architektonische Entscheidungen (ADRs) werden dort festgehalten.

---

## 🤖 5. Anweisungen für die KI (System Prompt)
1. **Analysiere** immer zuerst die bestehende Struktur, bevor du Code generierst.
2. **Verweigere** Implementierungen, die gegen die Asynchronität von Home Assistant verstoßen.
3. **Frage nach**, wenn Anforderungen unklar sind oder gegen HA-Beste-Praktiken verstoßen könnten.
4. **Handle proaktiv:** Wenn du einen Fehler im Parser findest, schlage sofort den Fix UND den passenden Test vor.
