"""MCP server exposing spectrometer tools."""

from __future__ import annotations

import os
from pathlib import Path

try:
    from mcp.server.fastmcp import FastMCP
except ModuleNotFoundError as exc:  # pragma: no cover - fallback for test environments without MCP SDK
    _MCP_IMPORT_ERROR = exc

    class FastMCP:  # type: ignore[override]
        def __init__(self, *_args, **_kwargs):
            self._missing_dependency = _MCP_IMPORT_ERROR

        def tool(self):
            def decorator(func):
                return func
            return decorator

        def run(self):
            raise ModuleNotFoundError(
                "The 'mcp' package is required to run the server. Install the project dependencies first."
            ) from self._missing_dependency

from .core import acquire_1d_spectrum_file, get_parameter_data

PACKAGE_ROOT = Path(__file__).resolve().parent
DEFAULT_DB_PATH = PACKAGE_ROOT.parent.parent / "db.csv"
DB_PATH = Path(os.environ.get("SPECTROMETER_DB_PATH", DEFAULT_DB_PATH))

mcp = FastMCP("spectrometer_mcp")


@mcp.tool()
def acquire_1d_spectrum(sample_holder: int | str, directory: str) -> str:
    """Copy the spectrum file referenced by Holder from db.csv into a target directory."""

    return acquire_1d_spectrum_file(sample_holder=sample_holder, directory=directory, db_path=DB_PATH)


@mcp.tool()
def get_parameter(filename: str) -> dict:
    """Return startPPM, endPPM and nPoints for a filename found in db.csv."""

    return get_parameter_data(filename=filename, db_path=DB_PATH)


if __name__ == "__main__":
    mcp.run()
