"""Operator preferences compose with inert metadata without changing CLI owners."""

import json
import os
import re
import subprocess
import sys
from pathlib import Path

import pytest


def _run_probe(*args, **kwargs):
    """Keep the original failure while exposing bounded phase/stack diagnostics."""
    try:
        return subprocess.run(*args, **kwargs)
    except subprocess.TimeoutExpired as error:
        stderr = error.stderr or b""
        if isinstance(stderr, bytes):
            stderr = stderr.decode("utf-8", errors="replace")
        # Do not echo arbitrary child logs, stdout, arguments or configuration.
        patterns = (
            r"\[cli-policy-probe\] phase=[a-z0-9:_-]+ elapsed=[0-9.]+s",
            r"Timeout \(\d+:\d+:\d+\)!",
            r"(?:Thread|Current thread) 0x[0-9a-fA-F]+ \(most recent call first\):",
            r'  File "[^"\r\n]+", line [0-9]+ in [^\r\n]+',
            r"  <no Python frame>",
        )
        lines = [
            line
            for line in stderr[-16384:].splitlines()
            if any(re.fullmatch(pattern, line) for pattern in patterns)
        ]
        diagnostic = "\n".join(lines) or "<no phase/stack diagnostics captured>"
        sys.stderr.write("CLI operator probe timeout diagnostics (bounded):\n")
        sys.stderr.write(diagnostic + "\n")
        sys.stderr.flush()
        raise


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
    result = _run_probe(
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
    # Assert
    assert result.returncode == 0, result.stderr
    assert json.loads(result.stdout)
