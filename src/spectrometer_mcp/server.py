"""MCP server exposing spectrometer tools."""

from __future__ import annotations

from dataclasses import dataclass
import os
from pathlib import Path
from typing import Any

try:
    from mcp.server.fastmcp import FastMCP
except ModuleNotFoundError as exc:  # pragma: no cover - fallback for test environments without MCP SDK
    _MCP_IMPORT_ERROR = exc

    class FastMCP:  # type: ignore[override]
        def __init__(self, *_args, **_kwargs):
            self._missing_dependency = _MCP_IMPORT_ERROR
            self.settings = type("Settings", (), {})()
            self._init_kwargs = _kwargs

        def tool(self):
            def decorator(func):
                return func
            return decorator

        def run(self, **_kwargs):
            raise ModuleNotFoundError(
                "The 'mcp' package is required to run the server. Install the project dependencies first."
            ) from self._missing_dependency

from .core import acquire_1d_spectrum_file, get_parameter_data, read_csv_file_data

PACKAGE_ROOT = Path(__file__).resolve().parent
DEFAULT_DB_PATH = PACKAGE_ROOT.parent.parent / "db.csv"
DB_PATH = Path(os.environ.get("SPECTROMETER_DB_PATH", DEFAULT_DB_PATH))
DEFAULT_TRANSPORT = "streamable-http"
DEFAULT_HOST = "0.0.0.0"
DEFAULT_PORT = 8000
SERVER_NAME = "spectrometer_mcp"


@dataclass(frozen=True)
class ServerConfig:
    transport: str = DEFAULT_TRANSPORT
    host: str = DEFAULT_HOST
    port: int = DEFAULT_PORT
    mount_path: str = "/mcp"

    @property
    def connector_path(self) -> str:
        normalized = self.mount_path if self.mount_path.startswith("/") else f"/{self.mount_path}"
        return f"{normalized.rstrip('/')}/"


def _default_mount_path(transport: str) -> str:
    if transport == "sse":
        return "/sse"
    return "/mcp"


def get_server_config_from_env() -> ServerConfig:
    transport = os.environ.get("MCP_TRANSPORT", DEFAULT_TRANSPORT).strip().lower()
    if transport not in {"streamable-http", "sse"}:
        raise ValueError("MCP_TRANSPORT must be either 'streamable-http' or 'sse'.")

    host = os.environ.get("MCP_HOST", DEFAULT_HOST).strip() or DEFAULT_HOST
    port_raw = os.environ.get("MCP_PORT", str(DEFAULT_PORT)).strip() or str(DEFAULT_PORT)
    try:
        port = int(port_raw)
    except ValueError as exc:
        raise ValueError("MCP_PORT must be an integer.") from exc

    mount_path = os.environ.get("MCP_MOUNT_PATH", _default_mount_path(transport)).strip() or _default_mount_path(transport)
    if not mount_path.startswith("/"):
        mount_path = f"/{mount_path}"

    return ServerConfig(transport=transport, host=host, port=port, mount_path=mount_path)


def _fastmcp_init_kwargs(config: ServerConfig) -> dict[str, object]:
    kwargs: dict[str, object] = {
        "host": config.host,
        "port": config.port,
        "mount_path": config.mount_path,
    }
    if config.transport == "streamable-http":
        kwargs["streamable_http_path"] = config.mount_path
    elif config.transport == "sse":
        kwargs["sse_path"] = config.mount_path
    return kwargs


def register_tools(server: Any) -> Any:
    server.tool()(acquire_1d_spectrum)
    server.tool()(get_parameter)
    server.tool()(read_csv_file)
    return server


mcp = None


@mcp.tool() if mcp else (lambda func: func)
def acquire_1d_spectrum(sample_holder: int | str, directory: str) -> str:
    """Transfer the sample from holder into the instrument and measures a 1d NMR spectrum"""

    return acquire_1d_spectrum_file(sample_holder=sample_holder, directory=directory, db_path=DB_PATH)


@mcp.tool() if mcp else (lambda func: func)
def get_parameter(filename: str) -> dict:
    """Return startPPM, endPPM and nPoints for a filename"""

    return get_parameter_data(filename=filename, db_path=DB_PATH)


@mcp.tool() if mcp else (lambda func: func)
def read_csv_file(filepath: str) -> list[dict[str, str]]:
    """Read a CSV file from a provided path and return its rows"""

    return read_csv_file_data(filepath=filepath)


def create_mcp_server(config: ServerConfig | None = None) -> Any:
    config = config or get_server_config_from_env()
    server = FastMCP(SERVER_NAME, **_fastmcp_init_kwargs(config))
    return register_tools(server)


def apply_server_config(server: Any, config: ServerConfig) -> None:
    server.settings.host = config.host
    server.settings.port = config.port
    server.settings.mount_path = config.mount_path

    if config.transport == "streamable-http":
        server.settings.streamable_http_path = config.mount_path
    elif config.transport == "sse":
        server.settings.sse_path = config.mount_path


def run_server(server: Any | None = None) -> None:
    config = get_server_config_from_env()
    server = create_mcp_server(config) if server is None else server
    apply_server_config(server, config)

    run_kwargs: dict[str, object] = {"transport": config.transport}
    if config.transport == "sse":
        run_kwargs["mount_path"] = config.mount_path

    server.run(**run_kwargs)


mcp = create_mcp_server(ServerConfig())


if __name__ == "__main__":
    run_server()
