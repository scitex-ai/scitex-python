"""Bundle inspection delegates to the installed expert without rewriting files."""

import hashlib
import json
import zipfile

import pytest
from click.testing import CliRunner

from scitex.cli.convert import convert


def _bundle(path, specification):
    with zipfile.ZipFile(path, "w") as archive:
        archive.writestr("spec.json", json.dumps(specification))
        archive.writestr("payload.csv", "x,y\n1,2\n")
    return path


def _spec(kind="figure", **fields):
    return {
        "schema": {"name": "scitex.bundle", "version": "2.0"},
        "type": kind,
        **fields,
    }


@pytest.mark.parametrize("kind", ["figure", "plot", "stats"])
def test_valid_bundle_is_accepted_by_the_domain_validator(tmp_path, kind):
    # Arrange
    path = _bundle(tmp_path / "valid.stx", _spec(kind))
    # Act
    result = CliRunner().invoke(convert, ["validate", str(path)])
    # Assert
    assert (result.exit_code, "Valid: 1, Invalid: 0" in result.output) == (0, True)


@pytest.mark.parametrize(
    "specification, reason",
    [
        (_spec(panels="invalid"), "'panels' must be a list"),
        (_spec("plot", axes=5), "'axes' must be a dictionary or list"),
        ({"type": "figure"}, "Missing required field: schema"),
        (_spec("unrecognized"), "Unknown bundle type"),
        (["not", "an", "object"], "spec.json must contain a JSON object"),
    ],
)
def test_invalid_bundle_reports_the_validation_reason(tmp_path, specification, reason):
    # Arrange
    path = _bundle(tmp_path / "invalid.stx", specification)
    # Act
    result = CliRunner().invoke(convert, ["validate", str(path)])
    # Assert
    assert (result.exit_code, reason in result.output) == (1, True)


def test_mixed_batch_reports_both_outcomes(tmp_path):
    # Arrange
    valid = _bundle(tmp_path / "valid.stx", _spec())
    invalid = _bundle(tmp_path / "invalid.stx", _spec(panels="invalid"))
    # Act
    result = CliRunner().invoke(convert, ["validate", str(valid), str(invalid)])
    # Assert
    assert (result.exit_code, "Valid: 1, Invalid: 1" in result.output) == (1, True)


def test_info_displays_the_real_archive_contents(tmp_path):
    # Arrange
    path = _bundle(tmp_path / "figure.stx", _spec(panels=[{"id": "A"}]))
    # Act
    result = CliRunner().invoke(convert, ["info", str(path)])
    # Assert
    assert (
        result.exit_code,
        "payload.csv" in result.output,
        "Panels: 1" in result.output,
    ) == (0, True, True)


@pytest.mark.parametrize("verb", ["info", "validate"])
def test_read_commands_preserve_the_archive_bytes(tmp_path, verb):
    # Arrange
    path = _bundle(tmp_path / "preserved.stx", _spec())
    before = hashlib.sha256(path.read_bytes()).hexdigest()
    # Act
    CliRunner().invoke(convert, [verb, str(path)])
    # Assert
    assert hashlib.sha256(path.read_bytes()).hexdigest() == before
