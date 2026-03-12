#!/usr/bin/env python3
"""Systematic tests for --json and --dry-run flags across the CLI.

Ensures every CLI group/command that declares --json outputs valid Result JSON,
and every mutation command with --dry-run returns a plan without side effects.
"""

import json
import os

import pytest
from click.testing import CliRunner

from scitex.cli.main import cli

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _parse_result(output: str) -> dict:
    """Parse CLI output as Result JSON. Raises on invalid JSON."""
    return json.loads(output.strip())


def _assert_result_envelope(data: dict):
    """Assert data conforms to the Result envelope schema."""
    assert "success" in data, f"Missing 'success' key in: {list(data.keys())}"
    assert isinstance(data["success"], bool)
    if data["success"]:
        assert "data" in data, "Successful Result must have 'data' key"


# ---------------------------------------------------------------------------
# 1. Root CLI --json tests
# ---------------------------------------------------------------------------


class TestRootCLIJson:
    """Test --json on the root `scitex` command."""

    def test_root_json_lists_commands(self):
        runner = CliRunner()
        result = runner.invoke(cli, ["--json"])
        assert result.exit_code == 0, result.output
        data = _parse_result(result.output)
        _assert_result_envelope(data)
        assert "commands" in data["data"]
        assert isinstance(data["data"]["commands"], dict)
        # Spot-check known subcommands
        cmds = data["data"]["commands"]
        for expected in ["dev", "scholar", "cloud", "writer", "plt", "stats"]:
            assert expected in cmds, f"'{expected}' missing from root --json"

    def test_root_json_help_recursive(self):
        runner = CliRunner()
        result = runner.invoke(cli, ["--json", "--help-recursive"])
        assert result.exit_code == 0, result.output
        data = _parse_result(result.output)
        _assert_result_envelope(data)
        # Should have subcommands tree
        assert "subcommands" in data["data"]
        subs = data["data"]["subcommands"]
        assert isinstance(subs, dict)
        assert "dev" in subs
        assert "scholar" in subs


# ---------------------------------------------------------------------------
# 2. Group-level --json tests (each group should list its subcommands)
# ---------------------------------------------------------------------------

_GROUP_COMMANDS = [
    "audio",
    "capture",
    "config",
    "convert",
    "dev",
    "docs",
    "introspect",
    "linter",
    "plt",
    "repro",
    "scholar",
    "security",
    "social",
    "stats",
    "template",
    "web",
]


class TestGroupJson:
    """Every click.Group should support --json and return Result with commands."""

    @pytest.mark.parametrize("group", _GROUP_COMMANDS)
    def test_group_json(self, group):
        runner = CliRunner()
        result = runner.invoke(cli, [group, "--json"])
        assert result.exit_code == 0, (
            f"`scitex {group} --json` failed (exit={result.exit_code}): "
            f"{result.output[:200]}"
        )
        data = _parse_result(result.output)
        _assert_result_envelope(data)
        assert "commands" in data["data"], (
            f"`scitex {group} --json` missing 'commands' in data"
        )


# Thin-wrapper groups that delegate via subprocess — they intercept bare --json
_THIN_WRAPPER_GROUPS = [
    "cloud",
    "writer",
    "tunnel",
    "linter",
    "dataset",
]


class TestThinWrapperGroupJson:
    """Thin-wrapper CLIs intercept --json and return Result with known commands."""

    @pytest.mark.parametrize("group", _THIN_WRAPPER_GROUPS)
    def test_thin_wrapper_json(self, group):
        runner = CliRunner()
        result = runner.invoke(cli, [group, "--json"])
        assert result.exit_code == 0, (
            f"`scitex {group} --json` failed (exit={result.exit_code}): "
            f"{result.output[:200]}"
        )
        data = _parse_result(result.output)
        _assert_result_envelope(data)
        assert "commands" in data["data"] or "package" in data["data"]


# ---------------------------------------------------------------------------
# 3. dev group --json + --help-recursive
# ---------------------------------------------------------------------------


class TestDevGroupJson:
    """Test dev group --json and --help-recursive combination."""

    def test_dev_json(self):
        runner = CliRunner()
        result = runner.invoke(cli, ["dev", "--json"])
        assert result.exit_code == 0, result.output
        data = _parse_result(result.output)
        _assert_result_envelope(data)
        cmds = data["data"]["commands"]
        for expected in ["clone", "config", "fix", "mcp", "test", "versions"]:
            assert expected in cmds

    def test_dev_json_help_recursive(self):
        runner = CliRunner()
        result = runner.invoke(cli, ["dev", "--json", "--help-recursive"])
        assert result.exit_code == 0, result.output
        data = _parse_result(result.output)
        _assert_result_envelope(data)
        assert "subcommands" in data["data"]
        subs = data["data"]["subcommands"]
        assert "clone" in subs
        assert "versions" in subs
        # Versions should have nested subcommands
        assert "subcommands" in subs["versions"]

    def test_dev_clone_json_dry_run(self):
        runner = CliRunner()
        result = runner.invoke(cli, ["dev", "clone", "--json", "--dry-run"])
        assert result.exit_code == 0, result.output
        data = _parse_result(result.output)
        _assert_result_envelope(data)
        assert data["data"]["action"] == "dry_run"
        assert "targets" in data["data"]


# ---------------------------------------------------------------------------
# 4. Leaf command --json tests
# ---------------------------------------------------------------------------


class TestLeafCommandJson:
    """Test --json on specific leaf commands."""

    def test_dev_versions_list_json(self):
        runner = CliRunner()
        result = runner.invoke(cli, ["dev", "versions", "list", "--json"])
        assert result.exit_code == 0, result.output
        data = json.loads(result.output.strip())
        assert isinstance(data, dict)

    def test_dev_versions_check_json(self):
        runner = CliRunner()
        result = runner.invoke(cli, ["dev", "versions", "check", "--json"])
        assert result.exit_code == 0, result.output
        data = json.loads(result.output.strip())
        assert isinstance(data, dict)

    def test_docs_tldr_json(self):
        runner = CliRunner()
        result = runner.invoke(cli, ["docs", "--tldr", "--json"])
        assert result.exit_code == 0, result.output
        data = _parse_result(result.output)
        _assert_result_envelope(data)
        assert "tldr" in data["data"]

    def test_docs_list_json(self):
        runner = CliRunner()
        result = runner.invoke(cli, ["docs", "--list", "--json"])
        assert result.exit_code == 0, result.output
        data = _parse_result(result.output)
        _assert_result_envelope(data)
        assert "pages" in data["data"]


# ---------------------------------------------------------------------------
# 5. --dry-run tests (mutation commands)
# ---------------------------------------------------------------------------

_DRY_RUN_COMMANDS = [
    # (args, expected_key_in_data)
    (["dev", "clone", "--dry-run"], "targets"),
    (["dev", "clone", "--dry-run", "--json"], "action"),
]


class TestDryRun:
    """Mutation commands with --dry-run should show plan without executing."""

    @pytest.mark.parametrize("args,expected_key", _DRY_RUN_COMMANDS)
    def test_dry_run_no_side_effects(self, args, expected_key):
        runner = CliRunner()
        result = runner.invoke(cli, args)
        assert result.exit_code == 0, (
            f"`scitex {' '.join(args)}` failed: {result.output[:200]}"
        )
        if "--json" in args:
            data = _parse_result(result.output)
            _assert_result_envelope(data)
            assert expected_key in data["data"]
        else:
            assert (
                "dry-run" in result.output.lower() or "dry_run" in result.output.lower()
            )

    def test_scholar_fetch_dry_run(self):
        """Scholar fetch --dry-run shows plan without downloading."""
        runner = CliRunner()
        result = runner.invoke(
            cli,
            ["scholar", "fetch", "10.1038/nature12373", "--dry-run"],
        )
        assert result.exit_code == 0, result.output
        assert (
            "dry-run" in result.output.lower() or "would fetch" in result.output.lower()
        )

    def test_scholar_fetch_dry_run_json(self):
        """Scholar fetch --dry-run --json returns plan as Result."""
        runner = CliRunner()
        result = runner.invoke(
            cli,
            ["scholar", "fetch", "10.1038/nature12373", "--dry-run", "--json"],
        )
        assert result.exit_code == 0, result.output
        data = _parse_result(result.output)
        _assert_result_envelope(data)
        assert data["data"]["action"] == "dry_run"

    def test_docs_build_dry_run(self):
        """Docs build --dry-run shows plan."""
        runner = CliRunner()
        result = runner.invoke(cli, ["docs", "build", "--dry-run"])
        assert result.exit_code == 0, result.output
        assert "dry-run" in result.output.lower()

    def test_docs_build_dry_run_json(self):
        """Docs build --dry-run --json returns plan as Result."""
        runner = CliRunner()
        result = runner.invoke(cli, ["docs", "build", "--dry-run", "--json"])
        assert result.exit_code == 0, result.output
        data = _parse_result(result.output)
        _assert_result_envelope(data)
        assert data["data"]["action"] == "dry_run"


# ---------------------------------------------------------------------------
# 6. help_recursive_to_json structure tests
# ---------------------------------------------------------------------------


class TestHelpRecursiveToJsonStructure:
    """Validate the structure of --json --help-recursive output."""

    def test_includes_params(self):
        """Each command in recursive JSON should have params."""
        runner = CliRunner()
        result = runner.invoke(cli, ["dev", "--json", "--help-recursive"])
        data = _parse_result(result.output)
        # The clone subcommand should list its params
        clone_info = data["data"]["subcommands"]["clone"]
        assert "params" in clone_info
        param_names = [p["name"] for p in clone_info["params"]]
        assert "package" in param_names
        assert "branch" in param_names
        assert "dry_run" in param_names
        assert "as_json" in param_names

    def test_nested_subgroups(self):
        """Nested subgroups should be fully expanded."""
        runner = CliRunner()
        result = runner.invoke(cli, ["dev", "--json", "--help-recursive"])
        data = _parse_result(result.output)
        versions = data["data"]["subcommands"]["versions"]
        assert "subcommands" in versions
        v_subs = versions["subcommands"]
        assert "list" in v_subs
        assert "check" in v_subs
        assert "sync" in v_subs

    def test_root_recursive_has_all_top_level(self):
        """Root --json --help-recursive should list all top-level commands."""
        runner = CliRunner()
        result = runner.invoke(cli, ["--json", "--help-recursive"])
        data = _parse_result(result.output)
        subs = data["data"]["subcommands"]
        for expected in ["dev", "scholar", "audio", "plt", "stats", "docs"]:
            assert expected in subs, f"'{expected}' missing from root recursive JSON"


# ---------------------------------------------------------------------------
# 7. Regression: --json should not break --help
# ---------------------------------------------------------------------------


class TestJsonDoesNotBreakHelp:
    """Ensure --json and --help coexist without errors."""

    def test_root_help_still_works(self):
        runner = CliRunner()
        result = runner.invoke(cli, ["--help"])
        assert result.exit_code == 0
        assert "Commands" in result.output

    def test_dev_help_still_works(self):
        runner = CliRunner()
        result = runner.invoke(cli, ["dev", "--help"])
        assert result.exit_code == 0
        assert "versions" in result.output

    def test_dev_help_recursive_still_works(self):
        runner = CliRunner()
        result = runner.invoke(cli, ["dev", "--help-recursive"])
        assert result.exit_code == 0
        assert "━━━" in result.output


if __name__ == "__main__":
    pytest.main([os.path.abspath(__file__), "-v"])
