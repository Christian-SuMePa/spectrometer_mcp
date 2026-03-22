# spectrometer_mcp

Minimaler Python-MCP-Server für Spektrumsdateien.

## Installation

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .[test]
```

## Remote-Server für ChatGPT starten

ChatGPT unterstützt für eigene MCP-Apps nur **Remote-MCP-Server** über **streaming HTTP** oder **SSE**. Deshalb ist der Server jetzt so konfigurierbar, dass er remote erreichbar gestartet werden kann.

### Empfohlener Start: streaming HTTP

#### Linux / macOS

```bash
MCP_TRANSPORT=streamable-http MCP_HOST=0.0.0.0 MCP_PORT=8000 MCP_MOUNT_PATH=/mcp python server.py
```

#### Windows cmd.exe

```bat
set MCP_TRANSPORT=streamable-http
set MCP_HOST=0.0.0.0
set MCP_PORT=8000
set MCP_MOUNT_PATH=/mcp
py server.py
```

Dann ist der Connector typischerweise unter dieser URL erreichbar:

```text
https://<deine-domain>/mcp/
```

### Alternative: SSE

#### Linux / macOS

```bash
MCP_TRANSPORT=sse MCP_HOST=0.0.0.0 MCP_PORT=8000 MCP_MOUNT_PATH=/sse python server.py
```

#### Windows cmd.exe

```bat
set MCP_TRANSPORT=sse
set MCP_HOST=0.0.0.0
set MCP_PORT=8000
set MCP_MOUNT_PATH=/sse
py server.py
```

Dann ist der Connector typischerweise unter dieser URL erreichbar:

```text
https://<deine-domain>/sse/
```

### Relevante Umgebungsvariablen

- `MCP_TRANSPORT`: `streamable-http` oder `sse`
- `MCP_HOST`: Netzwerk-Host, Standard `0.0.0.0`
- `MCP_PORT`: Netzwerk-Port, Standard `8000`
- `MCP_MOUNT_PATH`: HTTP-Pfad, Standard `/mcp` für streaming HTTP und `/sse` für SSE
- `SPECTROMETER_DB_PATH`: optionaler Pfad zu einer alternativen `db.csv`

## In ChatGPT verbinden

1. Stelle den Server unter einer öffentlich erreichbaren HTTPS-URL bereit.
2. Öffne in ChatGPT `Settings -> Apps -> Advanced settings -> Developer mode`.
3. Erstelle dort eine neue App für deinen Remote-MCP-Server.
4. Hinterlege als Server-URL z. B. `https://<deine-domain>/mcp/` oder `https://<deine-domain>/sse/`.
5. Aktiviere die App in einer Unterhaltung im Developer-Mode.

## MCP-Tools

- `acquire_1d_spectrum(sample_holder: int | str, directory: str) -> str`
- `get_parameter(filename: str) -> dict`
- `read_csv_file(filepath: str) -> list[dict[str, str]]`

## CSV-Dateien in ChatGPT lesen

Wenn der MCP-Server in ChatGPT verbunden ist, kannst du ChatGPT zum Beispiel so auffordern, die Datei über das MCP-Tool zu lesen:

```text
Nutze meine spectrometer_mcp App und rufe das Tool `read_csv_file` mit `filepath="/workspace/spectrometer_mcp/sample1.csv"` auf. Zeige mir danach den Inhalt der CSV-Datei.
```

Du übergibst der Funktion also einfach den vollständigen Pfad zur CSV-Datei. Das Tool liest die Datei und gibt die Zeilen als strukturierte Liste von Dictionaries zurück.
