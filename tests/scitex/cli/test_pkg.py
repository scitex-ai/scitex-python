#!/usr/bin/env python3
"""Tests for ``scitex.cli.pkg`` — the ``scitex-pkg audit`` CLI.

These tests mock the three subprocess primitives
(``_pip_show``, ``_python_import_ok``, ``_pip_install_editable``)
so no network, pip, or real python imports happen during test runs.
"""

from __future__ import annotations

import json
from unittest.mock import patch

import pytest
from click.testing import CliRunner

from scitex.cli.pkg import (
    DEFAULT_TARGET_PACKAGES,
    PackageAuditResult,
    _import_name,
    _repo_path_for,
    audit_package,
    pkg,
)


# ---------------------------------------------------------------------------
# Pure helper tests
# ---------------------------------------------------------------------------
class TestHelpers:
    """Sanity checks for the pure helpers."""

    def test_import_name_known(self):
        assert _import_name("scitex-orochi") == "scitex_orochi"
        assert _import_name("scitex-agent-container") == "scitex_agent_container"
        assert _import_name("scitex") == "scitex"

    def test_import_name_unknown_falls_back_to_dash_underscore(self):
        assert _import_name("totally-new-pkg") == "totally_new_pkg"

    def test_default_targets_include_required(self):
        # msg#16799 spec — guard against accidental deletion
        for required in (
            "scitex",
            "scitex-orochi",
            "scitex-agent-container",
            "scitex-clew",
            "scitex-cloud",
        ):
            assert required in DEFAULT_TARGET_PACKAGES

    def test_repo_path_for_scitex_prefers_scitex_python(self, tmp_path, monkeypatch):
        # Force root at tmp_path and create scitex-python dir
        monkeypatch.setenv("SCITEX_PROJ_ROOT", str(tmp_path))
        (tmp_path / "scitex-python").mkdir()
        assert _repo_path_for("scitex") == tmp_path / "scitex-python"

    def test_repo_path_for_other_pkg(self, tmp_path, monkeypatch):
        monkeypatch.setenv("SCITEX_PROJ_ROOT", str(tmp_path))
        (tmp_path / "scitex-orochi").mkdir()
        assert _repo_path_for("scitex-orochi") == tmp_path / "scitex-orochi"


# ---------------------------------------------------------------------------
# audit_package (the core engine)
# ---------------------------------------------------------------------------
class TestAuditPackageHappyPath:
    """pip show OK + import OK → status ok."""

    def test_ok(self):
        with patch("scitex.cli.pkg._pip_show", return_value="1.2.3"), patch(
            "scitex.cli.pkg._python_import_ok", return_value=(True, None)
        ):
            result = audit_package("scitex-orochi")
        assert result.status == "ok"
        assert result.version == "1.2.3"
        assert result.import_ok is True
        assert result.fix_attempted is False
        assert result.fix_result is None
        assert result.error is None


class TestAuditPackageDrift:
    """pip show OK but import fails → status drift."""

    def test_drift_without_auto_fix(self):
        with patch("scitex.cli.pkg._pip_show", return_value="1.2.3"), patch(
            "scitex.cli.pkg._python_import_ok",
            return_value=(False, "ModuleNotFoundError: no module named 'x'"),
        ):
            result = audit_package("scitex-orochi", auto_fix=False)
        assert result.status == "drift"
        assert result.version == "1.2.3"
        assert result.import_ok is False
        assert result.fix_attempted is False
        assert "ModuleNotFoundError" in (result.error or "")

    def test_drift_with_auto_fix_succeeds(self, tmp_path, monkeypatch):
        # Local repo exists
        monkeypatch.setenv("SCITEX_PROJ_ROOT", str(tmp_path))
        (tmp_path / "scitex-orochi").mkdir()

        # First import fails, then pip install -e succeeds, then re-import works
        import_calls = {"n": 0}

        def fake_import(_name):
            import_calls["n"] += 1
            if import_calls["n"] == 1:
                return (False, "boom")
            return (True, None)

        with patch(
            "scitex.cli.pkg._pip_show", side_effect=["1.2.3", "1.2.3"]
        ), patch(
            "scitex.cli.pkg._python_import_ok", side_effect=fake_import
        ), patch(
            "scitex.cli.pkg._pip_install_editable", return_value=(True, None)
        ) as mock_install:
            result = audit_package("scitex-orochi", auto_fix=True)

        mock_install.assert_called_once()
        assert result.fix_attempted is True
        assert result.fix_result == "succeeded"
        assert result.status == "ok"
        assert result.import_ok is True

    def test_drift_with_auto_fix_fails(self, tmp_path, monkeypatch):
        monkeypatch.setenv("SCITEX_PROJ_ROOT", str(tmp_path))
        (tmp_path / "scitex-orochi").mkdir()

        with patch("scitex.cli.pkg._pip_show", return_value="1.2.3"), patch(
            "scitex.cli.pkg._python_import_ok", return_value=(False, "boom")
        ), patch(
            "scitex.cli.pkg._pip_install_editable",
            return_value=(False, "pip: error"),
        ):
            result = audit_package("scitex-orochi", auto_fix=True)

        assert result.fix_attempted is True
        assert result.fix_result == "failed"
        assert result.status == "drift"
        assert "pip: error" in (result.error or "")

    def test_drift_with_auto_fix_but_no_repo(self, tmp_path, monkeypatch):
        # Point proj root at tmp with no repo dir — auto-fix should skip.
        monkeypatch.setenv("SCITEX_PROJ_ROOT", str(tmp_path))

        with patch("scitex.cli.pkg._pip_show", return_value="1.2.3"), patch(
            "scitex.cli.pkg._python_import_ok", return_value=(False, "boom")
        ), patch(
            "scitex.cli.pkg._pip_install_editable"
        ) as mock_install:
            result = audit_package("scitex-orochi", auto_fix=True)

        mock_install.assert_not_called()
        assert result.fix_attempted is False
        assert result.status == "drift"


class TestAuditPackageMissing:
    """pip show missing → status missing."""

    def test_missing(self):
        with patch("scitex.cli.pkg._pip_show", return_value=None), patch(
            "scitex.cli.pkg._python_import_ok", return_value=(False, "not found")
        ):
            result = audit_package("scitex-orochi")
        assert result.status == "missing"
        assert result.version is None
        assert result.import_ok is False


# ---------------------------------------------------------------------------
# CLI integration (click.testing.CliRunner)
# ---------------------------------------------------------------------------
class TestCliBasics:
    def test_pkg_help(self):
        runner = CliRunner()
        result = runner.invoke(pkg, ["--help"])
        assert result.exit_code == 0
        assert "audit" in result.output

    def test_audit_help(self):
        runner = CliRunner()
        result = runner.invoke(pkg, ["audit", "--help"])
        assert result.exit_code == 0
        assert "venv drift" in result.output.lower() or "drift" in result.output.lower()


class TestCliAllOk:
    def test_exit_zero_when_all_ok(self):
        runner = CliRunner()
        with patch("scitex.cli.pkg._pip_show", return_value="1.2.3"), patch(
            "scitex.cli.pkg._python_import_ok", return_value=(True, None)
        ):
            result = runner.invoke(pkg, ["audit", "--pkg", "scitex-orochi"])
        assert result.exit_code == 0
        assert "scitex-orochi" in result.output


class TestCliDriftExitCode:
    def test_exit_one_on_drift(self):
        runner = CliRunner()
        with patch("scitex.cli.pkg._pip_show", return_value="1.2.3"), patch(
            "scitex.cli.pkg._python_import_ok", return_value=(False, "bad")
        ):
            result = runner.invoke(
                pkg, ["audit", "--pkg", "scitex-orochi", "--quiet"]
            )
        assert result.exit_code == 1
        # quiet -> stdout should not contain status table
        assert "DRIFT" not in result.output

    def test_exit_two_on_fix_failure(self, tmp_path, monkeypatch):
        monkeypatch.setenv("SCITEX_PROJ_ROOT", str(tmp_path))
        (tmp_path / "scitex-orochi").mkdir()
        runner = CliRunner()
        with patch("scitex.cli.pkg._pip_show", return_value="1.2.3"), patch(
            "scitex.cli.pkg._python_import_ok", return_value=(False, "bad")
        ), patch(
            "scitex.cli.pkg._pip_install_editable",
            return_value=(False, "pip: error"),
        ):
            result = runner.invoke(
                pkg,
                ["audit", "--pkg", "scitex-orochi", "--auto-fix", "--quiet"],
            )
        assert result.exit_code == 2


class TestCliJsonOutput:
    def test_json_ndjson_schema(self):
        runner = CliRunner()
        with patch("scitex.cli.pkg._pip_show", return_value="1.2.3"), patch(
            "scitex.cli.pkg._python_import_ok", return_value=(True, None)
        ):
            result = runner.invoke(
                pkg, ["audit", "--pkg", "scitex-orochi", "--json"]
            )
        assert result.exit_code == 0
        lines = [line for line in result.output.splitlines() if line.strip()]
        assert len(lines) == 1
        payload = json.loads(lines[0])
        for key in (
            "pkg",
            "status",
            "repo_path",
            "version",
            "import_ok",
            "fix_attempted",
            "fix_result",
        ):
            assert key in payload
        assert payload["pkg"] == "scitex-orochi"
        assert payload["status"] == "ok"
        assert payload["version"] == "1.2.3"
        assert payload["import_ok"] is True

    def test_json_multi_package_ndjson(self):
        runner = CliRunner()
        with patch("scitex.cli.pkg._pip_show", return_value="1.2.3"), patch(
            "scitex.cli.pkg._python_import_ok", return_value=(True, None)
        ):
            result = runner.invoke(pkg, ["audit", "--json"])
        assert result.exit_code == 0
        lines = [line for line in result.output.splitlines() if line.strip()]
        # One line per default target package
        assert len(lines) == len(DEFAULT_TARGET_PACKAGES)
        for line in lines:
            payload = json.loads(line)
            assert payload["status"] == "ok"


class TestCliRemoteHostStub:
    def test_host_stub_says_not_implemented(self):
        runner = CliRunner()
        result = runner.invoke(pkg, ["audit", "--host", "mba"])
        # Exit 2 = error (not implemented)
        assert result.exit_code == 2


class TestCliQuietMode:
    def test_quiet_suppresses_human_output(self):
        runner = CliRunner()
        with patch("scitex.cli.pkg._pip_show", return_value="1.2.3"), patch(
            "scitex.cli.pkg._python_import_ok", return_value=(True, None)
        ):
            result = runner.invoke(
                pkg, ["audit", "--pkg", "scitex-orochi", "--quiet"]
            )
        assert result.exit_code == 0
        # No package-listing noise
        assert result.output.strip() == ""


class TestCliExtraPackagesFromEnv:
    def test_env_extra_packages_are_audited(self, monkeypatch):
        monkeypatch.setenv("SCITEX_PKG_AUDIT_EXTRA", "some-extra-pkg")
        runner = CliRunner()
        with patch("scitex.cli.pkg._pip_show", return_value="0.1.0"), patch(
            "scitex.cli.pkg._python_import_ok", return_value=(True, None)
        ):
            result = runner.invoke(pkg, ["audit", "--json"])
        assert result.exit_code == 0
        packages_in_output = {
            json.loads(line)["pkg"]
            for line in result.output.splitlines()
            if line.strip()
        }
        assert "some-extra-pkg" in packages_in_output
        # Defaults still present
        assert "scitex-orochi" in packages_in_output


if __name__ == "__main__":
    import os

    pytest.main([os.path.abspath(__file__)])

# EOF
