"""Real MCP protocol and persistence boundaries for owner-scoped exposure."""

import json
import os
import subprocess
import sys
from pathlib import Path

import pytest


@pytest.mark.parametrize(
    "operation",
    [
        "schema",
        "snapshot",
        "generic",
        "search",
        "inline",
        "skills",
        "docs",
        "resources",
    ],
)
def test_effective_mcp_policy_uses_actual_owner_and_owned_resources(
    tmp_path, operation
):
    # Arrange
    root = Path(__file__).resolve().parents[2]
    probe = Path(__file__).with_name("_mcp_exposure_probe.py")
    # Act
    result = subprocess.run(
        [sys.executable, "-B", str(probe), str(root / "src"), str(tmp_path), operation],
        capture_output=True,
        text=True,
        cwd=tmp_path,
        env=dict(os.environ, COVERAGE_FILE=str(tmp_path / ".coverage")),
        timeout=40,
    )
    # Assert
    assert result.returncode == 0, result.stderr
    assert json.loads(result.stdout)
