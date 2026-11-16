"""Audit installation consent with real processes and an inert pip protocol."""

import ast
import os
import subprocess
import sys
from pathlib import Path

import pytest


@pytest.fixture
def install_workspace(tmp_path):
    """Confine installation requests to a local pip module and receipt."""
    (tmp_path / "bin").mkdir()
    (tmp_path / "pip.py").write_text(
        "import sys\n"
        "from pathlib import Path\n"
        "Path('receipt.txt').write_text(repr(sys.argv[1:]))\n"
        "raise SystemExit(7 if Path('fail').exists() else 0)\n"
    )
    return tmp_path


def _invoke(workspace, flags):
    source = Path(__file__).resolve().parents[3] / "src/scitex/cli/audit.py"
    driver = (
        "import importlib.util,sys\n"
        "from click.testing import CliRunner\n"
        "spec=importlib.util.spec_from_file_location('audit_cli',sys.argv[1])\n"
        "module=importlib.util.module_from_spec(spec)\n"
        "spec.loader.exec_module(module)\n"
        "result=CliRunner().invoke(module.audit,['install',*sys.argv[2:]])\n"
        "print(repr((result.exit_code,result.output)))\n"
    )
    environment = dict(os.environ)
    environment.update(
        PATH=str(workspace / "bin"), COVERAGE_FILE=str(workspace / ".coverage")
    )
    process = subprocess.run(
        [sys.executable, "-c", driver, str(source), *flags],
        cwd=workspace,
        env=environment,
        capture_output=True,
        text=True,
        check=True,
    )
    return ast.literal_eval(process.stdout)


@pytest.mark.parametrize("flags", [[], ["--dry-run"], ["--yes", "--dry-run"]])
def test_preview_never_starts_installation(flags, install_workspace):
    # Arrange
    receipt = install_workspace / "receipt.txt"
    # Act
    code, output = _invoke(install_workspace, flags)
    # Assert
    assert (code, "Would install" in output, receipt.exists()) == (0, True, False)


def _provide_tools(workspace, names):
    for name in names:
        executable = workspace / "bin" / name
        executable.write_text("#!/bin/sh\nexit 99\n")
        executable.chmod(0o755)


def test_yes_installs_only_missing_python_tools(install_workspace):
    # Arrange
    _provide_tools(install_workspace, ["bandit"])
    # Act
    code, output = _invoke(install_workspace, ["--yes"])
    receipt = ast.literal_eval((install_workspace / "receipt.txt").read_text())
    # Assert
    assert (code, receipt, "requires system install" in output) == (
        0,
        ["install", "pip-audit"],
        True,
    )


def test_yes_preserves_an_already_complete_environment(install_workspace):
    # Arrange
    _provide_tools(install_workspace, ["bandit", "pip-audit", "shellcheck"])
    # Act
    code, output = _invoke(install_workspace, ["--yes"])
    # Assert
    assert (
        code,
        "already installed" in output,
        (install_workspace / "receipt.txt").exists(),
    ) == (0, True, False)


def test_failed_install_is_not_reported_as_success(install_workspace):
    # Arrange
    (install_workspace / "fail").touch()
    # Act
    code, output = _invoke(install_workspace, ["--yes"])
    receipt = ast.literal_eval((install_workspace / "receipt.txt").read_text())
    # Assert
    assert (code != 0, receipt, "Installed:" in output) == (
        True,
        ["install", "bandit", "pip-audit"],
        False,
    )
