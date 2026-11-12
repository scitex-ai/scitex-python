"""Conversion names preserve previews, JSON streams and metadata declines."""

import importlib.util
import json
from pathlib import Path

import pytest

_SPEC = importlib.util.spec_from_file_location(
    "_conversion_namespace_probes",
    Path(__file__).with_name("_public_exposure_helpers.py"),
)
_HELPERS = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(_HELPERS)
_probe = _HELPERS._probe
installed_parser = _HELPERS.installed_parser


def test_conversion_is_visible_and_old_verb_hidden(tmp_path):
    # Arrange
    request = {"args": ["--json"]}
    # Act
    result = _probe(tmp_path, "invoke", request)
    names = json.loads(result["stdout"])["data"]["commands"]
    # Assert
    assert (result["code"], "conversion" in names, "convert" in names) == (
        0,
        True,
        False,
    )


@pytest.mark.parametrize("group", ["conversion", "convert"])
@pytest.mark.parametrize("action", ["convert-file", "file"])
@pytest.mark.parametrize("flags", [[], ["--dry-run"], ["--yes", "--dry-run"]])
def test_canonical_and_legacy_previews_preserve_bytes_and_json(
    tmp_path, group, action, flags
):
    # Arrange
    source = tmp_path / "owned.figz"
    source.write_bytes(b"Owned preview input; not a qualified migration fixture")
    # Act
    result = _probe(
        tmp_path,
        "invoke",
        {
            "args": [group, action, str(source), *flags, "--json"],
        },
    )
    response = json.loads(result["stdout"]) if result["code"] == 0 else {}
    # Assert
    assert (
        result["code"],
        response.get("success"),
        source.read_bytes(),
        source.with_suffix(".stx").exists(),
    ) == (
        0,
        True,
        b"Owned preview input; not a qualified migration fixture",
        False,
    )
    assert response["data"]["action"] == "dry_run"
    assert bool(result["stderr"]) == (group == "convert" or action == "file")


def test_yes_reaches_actual_reader_instead_of_silently_previewing(tmp_path):
    # Arrange
    source = tmp_path / "invalid.figz"
    source.write_bytes(b"Not a ZIP archive")
    # Act
    result = _probe(
        tmp_path,
        "invoke",
        {
            "args": ["conversion", "convert-file", str(source), "--yes", "--json"],
        },
    )
    response = json.loads(result["stdout"])
    # Assert
    assert result["code"] != 0 and response["success"] is False
    assert "zip" in response["error"].lower()
    assert (
        source.read_bytes() == b"Not a ZIP archive"
        and not source.with_suffix(".stx").exists()
    )


@pytest.mark.parametrize("flags", [[], ["--yes", "--dry-run"]])
@pytest.mark.parametrize("as_json", [False, True])
def test_batch_preview_does_not_create_output_directory(tmp_path, flags, as_json):
    # Arrange
    source = tmp_path / "batch.figz"
    source.write_bytes(b"Owned batch preview")
    output = tmp_path / "must-not-create"
    # Act
    result = _probe(
        tmp_path,
        "invoke",
        {
            "args": [
                "conversion",
                "batch",
                str(source),
                "--output-dir",
                str(output),
                *flags,
                *(["--json"] if as_json else []),
            ],
        },
    )
    response = json.loads(result["stdout"]) if as_json else None
    # Assert
    assert (
        result["code"],
        response["success"] if as_json else "Would convert:" in result["stdout"],
        output.exists(),
        source.read_bytes(),
    ) == (
        0,
        True,
        False,
        b"Owned batch preview",
    )
    if as_json:
        assert response["data"]["files"][0]["status"] == "dry_run"


@pytest.mark.parametrize("declined", ["conversion", "convert"])
@pytest.mark.parametrize("group", ["conversion", "convert"])
def test_decline_reserves_both_conversion_names(
    tmp_path, installed_parser, declined, group
):
    # Arrange
    site, imported, called = installed_parser
    (site / "scitex_owned_parser-1.0.dist-info" / "entry_points.txt").write_text(
        f"[scitex.cli]\n{declined} = none\n"
    )
    # Act
    result = _probe(
        tmp_path,
        "invoke",
        {
            "args": [group, "--help"],
            "fixture_site": str(site),
        },
    )
    # Assert
    assert (result["code"] != 0, imported.exists(), called.exists()) == (
        True,
        False,
        False,
    )
