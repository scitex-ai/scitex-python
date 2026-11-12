"""Real module startup and canonical Dev declarations preserve CLI boundaries."""

import json
import os
import subprocess
import sys
from pathlib import Path

import pytest


def _environment(owned):
    environment = {
        key: value
        for key, value in os.environ.items()
        if not key.startswith("SCITEX_")
        and not any(
            part in key.upper() for part in ("TOKEN", "API_KEY", "PASSWORD", "SECRET")
        )
    }
    environment.update(
        HOME=str(owned),
        SCITEX_DIR=str(owned / "state"),
        XDG_RUNTIME_DIR=str(owned),
        COVERAGE_FILE=str(owned / ".coverage"),
        PYTHONDONTWRITEBYTECODE="1",
    )
    return environment


@pytest.mark.parametrize("flag", ["--help", "--json"])
@pytest.mark.parametrize(
    "malformed",
    [
        "config",
        "state",
        "packages_scalar",
        "packages_null",
        "package_entry",
        "package_name",
    ],
)
def test_real_module_startup_reports_invalid_preferences_without_traceback(
    tmp_path, flag, malformed
):
    # Arrange: ordinary python -m uses actual source and owned preference files.
    root = Path(__file__).resolve().parents[2]
    config, state = tmp_path / "config.yaml", tmp_path / "knobs.json"
    configurations = {
        "config": "packages:\n  - name: scitex-dev\n    cli_enabled: not-a-boolean\n",
        "state": "packages: []\n",
        "packages_scalar": "packages: not-a-list\n",
        "packages_null": "packages: null\n",
        "package_entry": "packages: [invalid-entry]\n",
        "package_name": "packages:\n  - cli_enabled: false\n",
    }
    config.write_text(configurations[malformed])
    state.write_text(
        json.dumps({"cli": {"scitex-dev": "false"}}) if malformed == "state" else "{}"
    )
    environment = _environment(tmp_path)
    environment.update(
        PYTHONPATH=str(root / "src"),
        SCITEX_DEV_CONFIG=str(config),
        SCITEX_DEV_KNOB_STATE=str(state),
    )
    # Act
    result = subprocess.run(
        [sys.executable, "-B", "-m", "scitex", flag],
        cwd=tmp_path,
        env=environment,
        capture_output=True,
        text=True,
        timeout=50,
    )
    # Assert
    assert (
        result.returncode,
        result.stdout,
        "Traceback" in result.stderr,
        "CLI exposure preferences" in result.stderr,
        "SCITEX_DEV_CONFIG" in result.stderr,
        "SCITEX_DEV_KNOB_STATE" in result.stderr,
    ) == (1, "", False, True, True, True), result.stderr


@pytest.mark.parametrize(
    "case",
    [
        "legacy",
        "declared",
        "none",
        "invalid",
        "ambiguous",
        "owner_false",
        "foreign_owner",
        "other_target",
    ],
)
def test_dev_composition_requires_real_canonical_owner_declaration(tmp_path, case):
    # Arrange: owned RECORD/entry points, with the genuine installed Dev object.
    root = Path(__file__).resolve().parents[2]
    probe = Path(__file__).with_name("_cli_operator_declared_dev_probe.py")
    # Act
    result = subprocess.run(
        [
            sys.executable,
            "-I",
            "-B",
            str(probe),
            str(root / "src"),
            str(tmp_path),
            case,
        ],
        cwd=tmp_path,
        env=_environment(tmp_path),
        capture_output=True,
        text=True,
        timeout=50,
    )
    # Assert
    assert result.returncode == 0, result.stderr
