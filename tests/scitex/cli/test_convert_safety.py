"""JSON bundle conversion must preserve the same file protections as text."""

import json
import zipfile

import pytest
from click.testing import CliRunner

from scitex.cli.convert import convert


def _legacy_bundle(path):
    with zipfile.ZipFile(path, "w") as archive:
        archive.writestr("spec.json", json.dumps({"schema": {"name": "legacy"}}))
        archive.writestr("data.csv", "x,y\n1,2\n")


def test_json_conversion_refuses_existing_output_without_overwrite(tmp_path):
    # Arrange
    source = tmp_path / "source.figz"
    target = tmp_path / "existing.stx"
    _legacy_bundle(source)
    target.write_bytes(b"owned output must remain unchanged")
    before = target.read_bytes()
    # Act
    result = CliRunner().invoke(
        convert, ["file", str(source), "--output", str(target), "--json"]
    )
    # Assert
    assert result.exit_code != 0 and target.read_bytes() == before
    assert json.loads(result.stdout)["success"] is False
    assert "Output file exists" in json.loads(result.stdout)["error"]


def test_json_conversion_validates_input_suffix_before_preview(tmp_path):
    # Arrange
    source = tmp_path / "source.txt"
    _legacy_bundle(source)
    # Act
    result = CliRunner().invoke(convert, ["file", str(source), "--dry-run", "--json"])
    # Assert
    assert result.exit_code != 0 and not source.with_suffix(".stx").exists()
    assert json.loads(result.stdout)["success"] is False


def test_json_existing_stx_is_a_nonwriting_noop(tmp_path):
    # Arrange
    source = tmp_path / "existing.stx"
    _legacy_bundle(source)
    before = source.read_bytes()
    # Act
    result = CliRunner().invoke(convert, ["file", str(source), "--json"])
    # Assert
    assert result.exit_code == 0 and source.read_bytes() == before
    assert json.loads(result.stdout)["data"]["action"] == "already_stx"


@pytest.mark.parametrize("as_json", [False, True])
def test_conversion_refuses_overwriting_the_source_through_a_hardlink(
    tmp_path, as_json
):
    # Arrange
    source = tmp_path / "source.figz"
    target = tmp_path / "alias.stx"
    _legacy_bundle(source)
    target.hardlink_to(source)
    before = source.read_bytes()
    args = ["file", str(source), "--output", str(target), "--overwrite"]
    if as_json:
        args.append("--json")
    # Act
    result = CliRunner().invoke(convert, args)
    # Assert
    assert result.exit_code != 0 and source.read_bytes() == before
    assert "same source file" in result.output


@pytest.mark.parametrize("as_json", [False, True])
def test_conversion_preview_preserves_input_without_creating_output(tmp_path, as_json):
    # Arrange
    source = tmp_path / "source.figz"
    _legacy_bundle(source)
    before = source.read_bytes()
    args = ["file", str(source), "--dry-run"]
    if as_json:
        args.append("--json")
    # Act
    result = CliRunner().invoke(convert, args)
    # Assert
    assert result.exit_code == 0 and source.read_bytes() == before
    assert not source.with_suffix(".stx").exists()
