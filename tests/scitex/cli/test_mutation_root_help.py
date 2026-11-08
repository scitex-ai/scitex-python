"""Shared mutation help must show runnable canonical umbrella examples."""

import os
import subprocess
import sys
from pathlib import Path

import pytest


@pytest.mark.parametrize(
    "path,expected",
    [
        (["dev", "audit", "install"], "scitex dev audit install --yes"),
        (
            ["dev", "template", "clone"],
            "scitex dev template clone pip-project ./my-package --yes",
        ),
    ],
)
def test_mutation_help_uses_the_canonical_umbrella_path(tmp_path, path, expected):
    # Arrange
    source = Path(__file__).resolve().parents[3] / "src"
    driver = (
        "import sys\n"
        "sys.path.insert(0,sys.argv[1])\n"
        "from click.testing import CliRunner\n"
        "from scitex.cli.main import cli\n"
        "result=CliRunner().invoke(cli,[*sys.argv[2:],'--help'],prog_name='scitex')\n"
        "print(result.output)\n"
        "raise SystemExit(result.exit_code)\n"
    )
    environment = dict(
        os.environ,
        HOME=str(tmp_path),
        SCITEX_DIR=str(tmp_path / "state"),
        COVERAGE_FILE=str(tmp_path / ".coverage"),
    )
    # Act
    result = subprocess.run(
        [sys.executable, "-I", "-c", driver, str(source), *path],
        cwd=tmp_path,
        env=environment,
        capture_output=True,
        text=True,
    )
    # Assert
    assert (
        result.returncode,
        "Examples:" in result.stdout,
        expected in result.stdout,
    ) == (
        0,
        True,
        True,
    )
