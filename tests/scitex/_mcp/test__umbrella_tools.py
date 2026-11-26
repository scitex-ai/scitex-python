#!/usr/bin/env python3
# File: tests/scitex/_mcp/test__umbrella_tools.py
"""Tests for the umbrella-only MCP tools in ``scitex._mcp._umbrella_tools``.

Under the stdio transport, stdout is the MCP protocol channel. Anything a
tool writes there lands in the JSON-RPC stream, so a tool must return its
result and must not write it to stdout.
"""

from __future__ import annotations

import json

import pytest

fastmcp = pytest.importorskip("fastmcp")
pytest.importorskip("scitex_template")


@pytest.fixture(scope="module")
def usage_show_tool():
    from scitex._mcp import get_tools_sync
    from scitex._mcp._umbrella_tools import register_umbrella_tools

    probe = fastmcp.FastMCP("umbrella-tools-probe")
    register_umbrella_tools(probe)
    return get_tools_sync(probe)["usage_show"]


def test_usage_show_tool_writes_nothing_to_stdout(usage_show_tool, capfd):
    # Arrange
    tool = usage_show_tool
    # Act
    tool.fn(topic="")
    captured = capfd.readouterr()
    # Assert
    assert captured.out == ""


def test_usage_show_tool_returns_the_usage_text(usage_show_tool):
    # Arrange
    from scitex.usage import _render

    tool = usage_show_tool
    # Act
    payload = json.loads(tool.fn(topic=""))
    # Assert
    assert payload["data"] == _render(None)


# EOF
