"""Foreground MCP serving and portable setup preserve legacy invocation."""

import json
import sys

from click.testing import CliRunner

from scitex.cli.mcp import mcp


def test_setup_is_a_complete_vendor_neutral_client_configuration():
    result = CliRunner().invoke(mcp, ["get-config", "--json"])
    assert result.exit_code == 0, result.output
    config = json.loads(result.stdout)
    assert config == {
        "mcpServers": {
            "scitex": {
                "command": sys.executable,
                "args": ["-m", "scitex", "mcp", "serve"],
            }
        }
    }
    assert "Claude" not in result.stdout


def test_legacy_setup_forwards_json_options_without_polluting_stdout():
    runner = CliRunner()
    current = runner.invoke(mcp, ["get-config", "--json"])
    legacy = runner.invoke(mcp, ["installation", "--json"])
    assert current.exit_code == legacy.exit_code == 0
    assert json.loads(current.stdout) == json.loads(legacy.stdout)
    assert legacy.stderr
    help_result = runner.invoke(mcp, ["installation", "--help"])
    assert help_result.exit_code == 0
    assert "--json" in help_result.stdout


def test_discovery_advertises_foreground_serve_and_preserves_old_help():
    visible = {
        name
        for name in mcp.list_commands(None)
        if not mcp.get_command(None, name).hidden
    }
    assert {"serve", "get-config"} <= visible
    assert not ({"start", "installation"} & visible)
    runner = CliRunner()
    for name in ["serve", "start"]:
        result = runner.invoke(mcp, [name, "--help"])
        assert result.exit_code == 0, result.output
        assert "--transport" in result.stdout
        assert "--host" in result.stdout
        assert "--port" in result.stdout


def test_recursive_help_keeps_retired_names_out_of_discovery():
    result = CliRunner().invoke(mcp, ["--help-recursive"])
    assert result.exit_code == 0, result.output
    assert "━━━ scitex mcp serve ━━━" in result.stdout
    assert "━━━ scitex mcp start ━━━" not in result.stdout
    assert "━━━ scitex mcp installation ━━━" not in result.stdout
