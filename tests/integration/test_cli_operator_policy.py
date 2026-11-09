"""Operator preferences compose with inert metadata without changing CLI owners."""

import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

from ._cli_probe_timeout import annotate_timeout


@pytest.mark.parametrize(
    "operation",
    [
        "default",
        "declined",
        "cross_surface",
        "owner_collision",
        "snapshot",
        "malformed",
        "malformed_config",
        "config_declined",
        "metadata_none",
        "reverse_snapshot",
    ],
)
def test_cli_operator_preferences_use_frozen_actual_owner_view(tmp_path, operation):
    # Arrange
    root = Path(__file__).resolve().parents[2]
    probe = Path(__file__).with_name("_cli_operator_policy_probe.py")
    environment = {
        key: value
        for key, value in os.environ.items()
        if not any(
            token in key.upper() for token in ("TOKEN", "API_KEY", "PASSWORD", "SECRET")
        )
    }
    environment["COVERAGE_FILE"] = str(tmp_path / ".coverage")
    # Act
    try:
        result = subprocess.run(
            [
                sys.executable,
                "-I",
                "-B",
                str(probe),
                str(root / "src"),
                str(tmp_path),
                operation,
            ],
            capture_output=True,
            text=True,
            cwd=tmp_path,
            env=environment,
            timeout=50,
        )
    except subprocess.TimeoutExpired as error:
        annotate_timeout(error)
        raise
    # Assert
    assert result.returncode == 0, result.stderr
    assert json.loads(result.stdout)
