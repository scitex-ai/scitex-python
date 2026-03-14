#!/usr/bin/env python3
# Timestamp: 2026-01-15
# File: tests/scitex/cli/test_mcp.py
"""Tests for scitex.cli.mcp module."""

import pytest
from click.testing import CliRunner

from scitex.cli.mcp import mcp


class TestMcpGroup:
    """Test MCP CLI group."""

    def test_mcp_help(self):
        """Test mcp --help."""
        runner = CliRunner()
        result = runner.invoke(mcp, ["--help"])
        assert result.exit_code == 0
        assert "MCP (Model Context Protocol)" in result.output
        assert "list" in result.output
        assert "doctor" in result.output
        assert "serve" in result.output


class TestMcpList:
    """Test mcp list command."""

    def test_list_help(self):
        """Test mcp list-tools --help."""
        runner = CliRunner()
        result = runner.invoke(mcp, ["list-tools", "--help"])
        assert result.exit_code == 0
        assert "--module" in result.output
        assert "--json" in result.output

    def test_list_all_tools(self):
        """Test mcp list-tools shows all tools."""
        runner = CliRunner()
        result = runner.invoke(mcp, ["list-tools"])
        assert result.exit_code == 0
        assert "SciTeX MCP" in result.output
        assert "audio" in result.output
        assert "scholar" in result.output

    def test_list_module_filter(self):
        """Test mcp list-tools --module filter."""
        runner = CliRunner()
        result = runner.invoke(mcp, ["list-tools", "--module", "audio"])
        assert result.exit_code == 0
        assert "audio:" in result.output
        assert "audio_speak" in result.output

    def test_list_invalid_module(self):
        """Test mcp list-tools with invalid module."""
        runner = CliRunner()
        result = runner.invoke(mcp, ["list-tools", "--module", "nonexistent"])
        assert result.exit_code == 1
        assert "Unknown module" in result.output

    def test_list_json_output(self):
        """Test mcp list-tools --json."""
        runner = CliRunner()
        result = runner.invoke(mcp, ["list-tools", "--json"])
        assert result.exit_code == 0
        assert '"total":' in result.output
        assert '"modules":' in result.output


class TestMcpDoctor:
    """Test mcp doctor command."""

    def test_doctor_help(self):
        """Test mcp doctor --help."""
        runner = CliRunner()
        result = runner.invoke(mcp, ["doctor", "--help"])
        assert result.exit_code == 0
        assert "--verbose" in result.output

    def test_doctor_basic(self):
        """Test mcp doctor runs."""
        runner = CliRunner()
        result = runner.invoke(mcp, ["doctor"])
        assert result.exit_code == 0
        assert "FastMCP" in result.output
        assert "OK" in result.output


class TestMcpServe:
    """Test mcp serve command."""

    def test_serve_help(self):
        """Test mcp start --help."""
        runner = CliRunner()
        result = runner.invoke(mcp, ["start", "--help"])
        assert result.exit_code == 0
        assert "--transport" in result.output
        assert "--host" in result.output
        assert "--port" in result.output
        assert "stdio" in result.output
        assert "sse" in result.output


class TestMcpHelpRecursive:
    """Test mcp help-recursive command."""

    def test_help_recursive(self):
        """Test mcp --help-recursive shows all commands."""
        runner = CliRunner()
        result = runner.invoke(mcp, ["--help-recursive"])
        assert result.exit_code == 0
        assert "scitex mcp" in result.output
        assert "scitex mcp list-tools" in result.output
        assert "scitex mcp doctor" in result.output
        assert "scitex mcp start" in result.output


# EOF
