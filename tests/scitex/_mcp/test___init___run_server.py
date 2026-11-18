#!/usr/bin/env python3
# File: tests/scitex/_mcp/test___init___run_server.py
"""Output-stream contract of ``scitex._mcp.run_server`` (PS-220).

Diagnostics go through scitex-logging on stderr. stdout stays empty, because
for the stdio transport stdout is the MCP protocol channel.
"""

from __future__ import annotations

import subprocess
import sys

import pytest

# Runs the real entry point in a fresh interpreter in which fastmcp cannot be
# imported -- a ``None`` entry in sys.modules makes ``import`` raise
# ImportError, exactly as on an install without the [mcp] extra.
_RUN_WITHOUT_FASTMCP = """
import sys
sys.modules["fastmcp"] = None
from scitex._mcp import run_server
run_server(transport="stdio")
"""


@pytest.fixture(scope="module")
def run_without_fastmcp():
    return subprocess.run(
        [sys.executable, "-c", _RUN_WITHOUT_FASTMCP],
        capture_output=True,
        text=True,
        timeout=300,
    )


def test_run_server_without_fastmcp_exits_one(run_without_fastmcp):
    # Arrange
    result = run_without_fastmcp
    # Act
    code = result.returncode
    # Assert
    assert code == 1


def test_run_server_without_fastmcp_reports_install_hint_on_stderr(
    run_without_fastmcp,
):
    # Arrange
    result = run_without_fastmcp
    # Act
    stderr = result.stderr
    # Assert
    assert "pip install fastmcp" in stderr


def test_run_server_without_fastmcp_writes_nothing_to_stdout(run_without_fastmcp):
    # Arrange
    result = run_without_fastmcp
    # Act
    stdout = result.stdout
    # Assert
    assert stdout == ""


# EOF
