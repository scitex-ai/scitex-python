"""Package validation keeps real interpreter checks and compatibility routes."""

import json
from importlib.metadata import version

from click.testing import CliRunner

from scitex.cli.pkg import audit_package, pkg


def test_package_validation_is_visible_and_old_audit_is_hidden():
    # Arrange
    runner = CliRunner()
    # Act
    result = runner.invoke(pkg, ["--help"])
    # Assert
    assert result.exit_code == 0
    assert "validate" in result.stdout
    assert "\n  audit " not in result.stdout


def test_validation_checks_a_real_installed_distribution_without_pip():
    # Arrange
    expected_version = version("click")
    # Act
    result = audit_package("click")
    # Assert
    assert (result.status, result.version, result.import_ok, result.fix_attempted) == (
        "ok", expected_version, True, False
    )


def test_canonical_and_legacy_routes_keep_real_json_results(tmp_path, monkeypatch):
    # Arrange
    monkeypatch.setenv("XDG_RUNTIME_DIR", str(tmp_path))
    runner = CliRunner()
    # Act
    canonical = runner.invoke(pkg, ["validate", "--pkg", "click", "--json"])
    legacy = runner.invoke(pkg, ["audit", "--pkg", "click", "--json"])
    # Assert
    assert canonical.exit_code == legacy.exit_code == 0
    assert json.loads(canonical.stdout) == json.loads(legacy.stdout)
    assert json.loads(canonical.stdout)["status"] == "ok"
    assert "deprecated" in legacy.stderr.lower()


def test_invalid_distribution_name_cannot_execute_import_statements(tmp_path, monkeypatch):
    # Arrange
    monkeypatch.chdir(tmp_path)
    marker = tmp_path / "owned_marker"
    value = "os;__import__('pathlib').Path('owned_marker').write_text('unexpected')#"
    # Act
    result = audit_package(value)
    # Assert
    assert not marker.exists()
    assert result.status == "missing"
    assert "invalid" in result.error.lower()
    assert not result.fix_attempted


def test_missing_distribution_is_not_reported_as_valid():
    # Arrange
    name = "scitex-test-absent-distribution-1109"
    # Act
    result = audit_package(name)
    # Assert
    assert (result.status, result.version, result.import_ok, result.fix_attempted) == (
        "missing", None, False, False
    )
