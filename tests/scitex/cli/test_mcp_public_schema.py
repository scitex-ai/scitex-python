"""Discover real MCP tools through the public Dev schema export without running tools."""

from __future__ import annotations

import json

import pytest
from click.testing import CliRunner

pytest.importorskip("fastmcp")
pytest.importorskip("scitex_dev")


@pytest.fixture(scope="module")
def actual_discovery():
    from scitex.cli.mcp import mcp

    return CliRunner().invoke(mcp, ["list-tools", "--json"])


def test_actual_json_discovery_succeeds(actual_discovery):
    # Arrange
    result = actual_discovery
    # Act
    exit_code = result.exit_code
    # Assert
    assert exit_code == 0, result.output


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
