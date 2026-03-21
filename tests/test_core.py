from __future__ import annotations

from pathlib import Path

import pytest

from spectrometer_mcp.core import (
    DatabaseNotFoundError,
    FilenameNotFoundError,
    SpectrumSourceMissingError,
    TargetDirectoryNotFoundError,
    UnknownHolderError,
    acquire_1d_spectrum_file,
    get_parameter_data,
)

FIXTURES = Path(__file__).parent / "fixtures"
DB_PATH = FIXTURES / "db.csv"


@pytest.fixture()
def db_dir(tmp_path: Path) -> Path:
    db_dir = tmp_path / "data"
    db_dir.mkdir()
    (db_dir / "db.csv").write_text(DB_PATH.read_text(encoding="utf-8"), encoding="utf-8")
    (db_dir / "sample1.csv").write_text((FIXTURES / "spectra" / "sample1.csv").read_text(encoding="utf-8"), encoding="utf-8")
    (db_dir / "sample2.csv").write_text((FIXTURES / "spectra" / "sample2.csv").read_text(encoding="utf-8"), encoding="utf-8")
    return db_dir


def test_acquire_1d_spectrum_copies_file(db_dir: Path, tmp_path: Path) -> None:
    destination_dir = tmp_path / "out"
    destination_dir.mkdir()

    result = acquire_1d_spectrum_file(1, str(destination_dir), db_dir / "db.csv")

    destination = Path(result)
    assert destination == (destination_dir / "sample1.csv").resolve()
    assert destination.read_text(encoding="utf-8").startswith("ppm,intensity")


def test_acquire_1d_spectrum_rejects_unknown_holder(db_dir: Path, tmp_path: Path) -> None:
    destination_dir = tmp_path / "out"
    destination_dir.mkdir()

    with pytest.raises(UnknownHolderError, match="Unknown Holder"):
        acquire_1d_spectrum_file("99", str(destination_dir), db_dir / "db.csv")


def test_acquire_1d_spectrum_requires_existing_db(tmp_path: Path) -> None:
    destination_dir = tmp_path / "out"
    destination_dir.mkdir()

    with pytest.raises(DatabaseNotFoundError, match="db.csv not found"):
        acquire_1d_spectrum_file(1, str(destination_dir), tmp_path / "db.csv")


def test_acquire_1d_spectrum_requires_existing_source(db_dir: Path, tmp_path: Path) -> None:
    destination_dir = tmp_path / "out"
    destination_dir.mkdir()
    (db_dir / "sample1.csv").unlink()

    with pytest.raises(SpectrumSourceMissingError, match="Spectrum source file not found"):
        acquire_1d_spectrum_file(1, str(destination_dir), db_dir / "db.csv")


def test_acquire_1d_spectrum_requires_existing_target_directory(db_dir: Path, tmp_path: Path) -> None:
    missing_directory = tmp_path / "missing"

    with pytest.raises(TargetDirectoryNotFoundError, match="Target directory does not exist"):
        acquire_1d_spectrum_file(1, str(missing_directory), db_dir / "db.csv")


def test_get_parameter_returns_expected_fields(db_dir: Path) -> None:
    result = get_parameter_data("/tmp/results/sample2.csv", db_dir / "db.csv")

    assert result == {"startPPM": 8.0, "endPPM": 0.0, "nPoints": 1024}


def test_get_parameter_rejects_unknown_filename(db_dir: Path) -> None:
    with pytest.raises(FilenameNotFoundError, match="Filename not found in db.csv"):
        get_parameter_data("/tmp/results/missing.csv", db_dir / "db.csv")
