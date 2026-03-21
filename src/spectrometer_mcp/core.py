"""Core file operations for the spectrometer MCP server."""

from __future__ import annotations

from csv import DictReader
from pathlib import Path
import shutil
from typing import Any


class SpectrometerDataError(Exception):
    """Base class for data-related spectrometer errors."""


class DatabaseNotFoundError(SpectrometerDataError):
    """Raised when db.csv is missing."""


class UnknownHolderError(SpectrometerDataError):
    """Raised when a holder is not present in db.csv."""


class SpectrumSourceMissingError(SpectrometerDataError):
    """Raised when the source spectrum file referenced in db.csv is missing."""


class FilenameNotFoundError(SpectrometerDataError):
    """Raised when a filename is not present in db.csv."""


class TargetDirectoryNotFoundError(SpectrometerDataError):
    """Raised when the destination directory does not exist."""


class CsvFileNotFoundError(SpectrometerDataError):
    """Raised when a requested CSV file does not exist."""


def _load_db_rows(db_path: Path) -> list[dict[str, str]]:
    if not db_path.is_file():
        raise DatabaseNotFoundError(f"db.csv not found: {db_path}")

    with db_path.open("r", encoding="utf-8", newline="") as handle:
        return list(DictReader(handle))


def _find_row_by_field(rows: list[dict[str, str]], field: str, value: str) -> dict[str, str]:
    for row in rows:
        if row.get(field) == value:
            return row
    if field == "Holder":
        raise UnknownHolderError(f"Unknown Holder: {value}")
    raise FilenameNotFoundError(f"Filename not found in db.csv: {value}")


def acquire_1d_spectrum_file(sample_holder: int | str, directory: str, db_path: Path) -> str:
    target_directory = Path(directory)
    if not target_directory.is_dir():
        raise TargetDirectoryNotFoundError(f"Target directory does not exist: {target_directory}")

    rows = _load_db_rows(db_path)
    row = _find_row_by_field(rows, "Holder", str(sample_holder))
    filename = row.get("Filename")
    if not filename:
        raise SpectrumSourceMissingError(f"Missing Filename value for Holder: {sample_holder}")

    source_path = db_path.parent / filename
    if not source_path.is_file():
        raise SpectrumSourceMissingError(f"Spectrum source file not found: {source_path}")

    destination = target_directory / source_path.name
    shutil.copy2(source_path, destination)
    return str(destination.resolve())


def get_parameter_data(filename: str, db_path: Path) -> dict[str, Any]:
    rows = _load_db_rows(db_path)
    basename = Path(filename).name
    row = _find_row_by_field(rows, "Filename", basename)
    return {
        "startPPM": _parse_numeric_value(row.get("startPPM"), "startPPM", basename),
        "endPPM": _parse_numeric_value(row.get("endPPM"), "endPPM", basename),
        "nPoints": _parse_numeric_value(row.get("nPoints"), "nPoints", basename, as_int=True),
    }


def read_csv_file_data(filepath: str) -> list[dict[str, str]]:
    csv_path = Path(filepath)
    if not csv_path.is_file():
        raise CsvFileNotFoundError(f"CSV file not found: {csv_path}")

    with csv_path.open("r", encoding="utf-8", newline="") as handle:
        return list(DictReader(handle))


def _parse_numeric_value(raw_value: str | None, field: str, filename: str, *, as_int: bool = False) -> int | float:
    if raw_value is None or raw_value == "":
        raise FilenameNotFoundError(f"Missing {field} value for Filename: {filename}")

    try:
        return int(raw_value) if as_int else float(raw_value)
    except ValueError as exc:
        raise FilenameNotFoundError(
            f"Invalid {field} value for Filename {filename}: {raw_value}"
        ) from exc
