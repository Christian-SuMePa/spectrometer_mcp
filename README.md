# spectrometer_mcp

Minimaler Python-MCP-Server für Spektrumsdateien.

## Installation

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .[test]
```

## Server starten

Standardmäßig wird `db.csv` im Repository-Root verwendet. Optional kann über `SPECTROMETER_DB_PATH` ein anderer Pfad gesetzt werden.

```bash
python server.py
```

oder

```bash
python -m spectrometer_mcp.server
```

## MCP-Tools

- `acquire_1d_spectrum(sample_holder: int | str, directory: str) -> str`
- `get_parameter(filename: str) -> dict`
- `read_csv_file(filepath: str) -> list[dict[str, str]]`

## CSV-Dateien in ChatGPT lesen

Wenn der MCP-Server in ChatGPT verbunden ist, kannst du ChatGPT zum Beispiel so auffordern, die Datei über das MCP-Tool zu lesen:

```text
Rufe das MCP-Tool `read_csv_file` mit `filepath="/workspace/spectrometer_mcp/sample1.csv"` auf und zeige mir den Inhalt der CSV-Datei.
```

Du übergibst der Funktion also einfach den vollständigen Pfad zur CSV-Datei. Das Tool liest die Datei und gibt die Zeilen als strukturierte Liste von Dictionaries zurück.
