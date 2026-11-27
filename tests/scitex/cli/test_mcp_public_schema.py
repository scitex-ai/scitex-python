"""Discover real MCP tools through the public Dev schema export without running tools."""

from __future__ import annotations

import importlib.util
import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

pytest.importorskip("fastmcp")
pytest.importorskip("scitex_dev")


@pytest.fixture(scope="module")
def actual_discovery():
    source_root = str(Path(importlib.util.find_spec("scitex").origin).parent.parent)
    env = os.environ.copy()
    env["PYTHONPATH"] = os.pathsep.join(
        filter(None, (source_root, env.get("PYTHONPATH")))
    )
    return subprocess.run(
        [sys.executable, "-m", "scitex", "mcp", "list-tools", "--json"],
        capture_output=True,
        text=True,
        timeout=45,
        env=env,
    )


def test_actual_json_discovery_succeeds(actual_discovery):
    # Arrange
    result = actual_discovery
    # Act
    exit_code = result.returncode
    # Assert
    assert exit_code == 0, result.stderr


def test_actual_json_discovery_uses_public_result_schema(actual_discovery):
    # Arrange
    from scitex_dev import RESULT_SCHEMA

    # Act
    payload = json.loads(actual_discovery.stdout)
    # Assert
    assert payload["result_envelope"] == RESULT_SCHEMA


def test_actual_json_discovery_contains_tools(actual_discovery):
    # Arrange
    result = actual_discovery
    # Act
    payload = json.loads(result.stdout)
    # Assert
    assert payload["total"] > 0
