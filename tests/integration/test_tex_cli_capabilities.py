"""TeX commands describe the installed provider's actual capabilities."""

import json

import pytest
import yaml
from click.testing import CliRunner

from scitex.cli.tex import tex


def test_vector_formatter_returns_machine_readable_mathematical_notation():
    # Arrange
    runner = CliRunner()
    # Act
    result = runner.invoke(tex, ["format-vector", "AB", "--json"])
    data = json.loads(result.stdout)["data"] if result.exit_code == 0 else {}
    # Assert
    assert (result.exit_code, data.get("vector")) == (
        0,
        r"\overrightarrow{\mathrm{AB}}",
    )


def test_recursive_help_advertises_supported_capabilities_without_legacy_file_routes():
    # Arrange
    runner = CliRunner()
    # Act
    result = runner.invoke(tex, ["--help-recursive"])
    # Assert
    assert (
        result.exit_code,
        "━━━ scitex tex format-vector ━━━" in result.stdout,
        "━━━ scitex tex render-preview ━━━" in result.stdout,
        "━━━ scitex tex preview ━━━" in result.stdout,
        "━━━ scitex tex to-vec ━━━" in result.stdout,
    ) == (0, True, True, False, False)


def test_expression_preview_writes_an_image_and_replayable_recipe(tmp_path):
    # Arrange
    target = tmp_path / "expressions.png"
    # Act
    result = CliRunner().invoke(
        tex, ["render-preview", "x^2", "y^2", "--output", str(target), "--yes"]
    )
    # Assert
    assert (
        result.exit_code,
        target.read_bytes()[:8] if target.exists() else None,
        (
            len(yaml.safe_load(target.with_suffix(".yaml").read_text())["axes"])
            if target.with_suffix(".yaml").exists()
            else None
        ),
    ) == (0, b"\x89PNG\r\n\x1a\n", 2)


def test_expression_preview_dry_run_does_not_create_output(tmp_path):
    # Arrange
    target = tmp_path / "absent" / "preview.png"
    # Act
    result = CliRunner().invoke(
        tex, ["render-preview", "x^2", "--output", str(target), "--dry-run", "--yes"]
    )
    # Assert
    assert (result.exit_code, target.parent.exists()) == (0, False)


@pytest.mark.parametrize("command", ["preview", "to-vec"])
def test_unsupported_legacy_file_routes_report_a_typed_migration(tmp_path, command):
    # Arrange
    source = tmp_path / "paper.tex"
    source.write_text("owned source")
    # Act
    result = CliRunner().invoke(tex, [command, str(source)])
    # Assert
    assert (
        result.exit_code,
        "Error:" in result.output,
        "scitex tex" in result.output,
    ) == (
        2,
        True,
        True,
    )
