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
