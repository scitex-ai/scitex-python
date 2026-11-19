#!/usr/bin/env python3
# File: ./tests/scitex/cli/test__deprecation.py

"""Renamed umbrella commands and their hidden aliases (_deprecation.py).

CLI standardization (noun/verb convention, 2026-11-19). Covers:
- renamed commands are mounted under their canonical names,
- every old name is a hidden alias that still works and prints a one-line
  deprecation note to stderr.
The new flags and root help are covered in test_main.py.

No mocks: every case runs the real click app through CliRunner, and
environment variables are set with CliRunner's own ``env=``. The
deprecation note is printed once per shell session (scitex-dev keys a
marker file on the parent PID under $XDG_RUNTIME_DIR), so each test gets
its own XDG_RUNTIME_DIR.
"""

import json

import click
import pytest
from click.testing import CliRunner

from scitex.cli.main import cli


@pytest.fixture
def invoke(tmp_path_factory):
    """Run the CLI in a fresh shell session (own $XDG_RUNTIME_DIR)."""
    runtime = tmp_path_factory.mktemp("runtime")

    def _run(args, env=None, **kwargs):
        merged = {"XDG_RUNTIME_DIR": str(runtime), **(env or {})}
        return CliRunner().invoke(
            cli, args, catch_exceptions=False, env=merged, **kwargs
        )

    return _run


def _stdout_json(result):
    return json.loads(result.stdout)


def _resolve(path):
    """Walk the real command tree; return the command at ``path``."""
    ctx = click.Context(cli, info_name="scitex")
    node = cli
    for part in path:
        node = node.get_command(ctx, part)
        assert node is not None, f"no command {' '.join(path)!r}"
        ctx = click.Context(node, info_name=part, parent=ctx)
    return node


# --------------------------------------------------------------------------- #
# Renamed commands                                                             #
# --------------------------------------------------------------------------- #

RENAMED = [
    # (canonical path, old path)
    (["audit-security"], ["audit"]),
    (["audit-tool", "status"], ["audit", "status"]),
    (["audit-tool", "install"], ["audit", "install"]),
    (["bundle"], ["convert"]),
    (["bundle", "convert"], ["convert", "file"]),
    (["introspection"], ["introspect"]),
    (["introspection", "show-signature"], ["introspect", "q"]),
    (["introspection", "show-source"], ["introspect", "qq"]),
    (["introspection", "list-members"], ["introspect", "dir"]),
    (["introspection", "list-api"], ["introspect", "api"]),
    (["introspection", "show-docstring"], ["introspect", "docstring"]),
    (["introspection", "list-exports"], ["introspect", "exports"]),
    (["introspection", "find-examples"], ["introspect", "examples"]),
    (["introspection", "show-hierarchy"], ["introspect", "hierarchy"]),
    (["introspection", "show-hints"], ["introspect", "hints"]),
    (["introspection", "list-imports"], ["introspect", "imports"]),
    (["introspection", "list-deps"], ["introspect", "deps"]),
    (["introspection", "show-calls"], ["introspect", "calls"]),
    (["event", "list"], ["event", "history"]),
    (["event", "show-latest"], ["event", "latest"]),
    (["event", "list-types"], ["event", "types"]),
    (["resource", "show-specs"], ["resource", "specs"]),
    (["resource", "show-usage"], ["resource", "usage"]),
    (["repro", "get-id"], ["repro", "gen-id"]),
    (["repro", "get-timestamp"], ["repro", "gen-timestamp"]),
    (["mcp", "show-installation"], ["mcp", "installation"]),
    (["tex", "convert-to-vector"], ["tex", "to-vec"]),
]

class TestRenamedCommands:
    @pytest.mark.parametrize(
        "new", [n for n, _ in RENAMED], ids=[" ".join(n) for n, _ in RENAMED]
    )
    def test_canonical_name_is_a_visible_command(self, new):
        # Arrange
        path = new
        # Act
        command = _resolve(path)
        # Assert
        assert not command.hidden

    @pytest.mark.parametrize(
        "old",
        [
            ["audit"],
            ["introspect"],
            ["convert"],
            ["introspection", "q"],
            ["introspection", "qq"],
            ["introspection", "dir"],
            ["introspection", "api"],
            ["introspection", "docstring"],
            ["introspection", "exports"],
            ["introspection", "examples"],
            ["introspection", "hierarchy"],
            ["introspection", "hints"],
            ["introspection", "imports"],
            ["introspection", "deps"],
            ["introspection", "calls"],
            ["bundle", "file"],
            ["event", "history"],
            ["event", "latest"],
            ["event", "types"],
            ["resource", "specs"],
            ["resource", "usage"],
            ["repro", "gen-id"],
            ["repro", "gen-timestamp"],
            ["mcp", "installation"],
            ["tex", "to-vec"],
        ],
        ids=lambda p: " ".join(p),
    )
    def test_old_name_is_a_hidden_deprecated_alias(self, old):
        # Arrange
        path = old
        # Act
        command = _resolve(path)
        # Assert
        assert command.hidden and command._deprecated_alias["remove_in"] == "3.0"

    @pytest.mark.parametrize(
        "group,old", [([], "introspect"), ([], "convert"), (["event"], "history")]
    )
    def test_old_name_is_not_listed_in_help(self, invoke, group, old):
        # Arrange
        args = [*group, "--help"]
        # Act
        result = invoke(args)
        # Assert
        assert f"\n  {old} " not in result.stdout


# --------------------------------------------------------------------------- #
# Old names keep working, with a one-line deprecation note on stderr          #
# --------------------------------------------------------------------------- #


class TestAliasesForward:
    @pytest.mark.parametrize("new,old", RENAMED, ids=[" ".join(o) for _, o in RENAMED])
    def test_old_path_reaches_the_new_help(self, invoke, new, old):
        # Arrange
        args = [*old, "--help"]
        # Act
        result = invoke(args)
        # Assert
        assert result.exit_code == 0

    def test_leaf_alias_runs_the_new_command(self, invoke):
        # Arrange
        args = ["repro", "gen-id", "--count", "3"]
        # Act
        result = invoke(args)
        # Assert
        assert result.exit_code == 0 and len(result.stdout.split()) == 3

    def test_leaf_alias_prints_one_deprecation_line_to_stderr(self, invoke):
        # Arrange
        args = ["repro", "gen-id"]
        # Act
        result = invoke(args)
        # Assert
        assert result.stderr.splitlines() == [
            "'gen-id' is deprecated — use 'get-id' (removed in v3.0)"
        ]

    def test_leaf_alias_keeps_stdout_free_of_the_note(self, invoke):
        # Arrange
        args = ["repro", "gen-timestamp", "--format", "file"]
        # Act
        result = invoke(args)
        # Assert
        assert "deprecated" not in result.stdout

    def test_group_alias_forwards_old_leaf_names(self, invoke):
        # Arrange
        args = ["introspect", "q", "json.dumps"]
        # Act
        result = invoke(args)
        # Assert
        assert result.exit_code == 0 and "dumps(" in result.stdout

    def test_group_and_leaf_alias_each_note_once(self, invoke):
        # Arrange
        args = ["introspect", "q", "json.dumps"]
        # Act
        result = invoke(args)
        # Assert
        assert result.stderr.splitlines() == [
            "'introspect' is deprecated — use 'introspection' (removed in v3.0)",
            "'q' is deprecated — use 'show-signature' (removed in v3.0)",
        ]

    def test_group_alias_forwards_help_to_the_new_group(self, invoke):
        # Arrange
        args = ["introspect", "--help"]
        # Act
        result = invoke(args)
        # Assert
        assert "show-signature" in result.stdout

    def test_split_audit_alias_routes_status_to_audit_tool(self, invoke):
        # Arrange
        args = ["audit", "status", "--json"]
        # Act
        result = invoke(args)
        # Assert
        assert "bandit" in _stdout_json(result)

    def test_split_audit_alias_names_the_new_command(self, invoke):
        # Arrange
        args = ["audit", "status"]
        # Act
        result = invoke(args)
        # Assert
        assert result.stderr.splitlines() == [
            "'audit' is deprecated — use 'audit-tool status' (removed in v3.0)"
        ]

    def test_split_audit_alias_routes_path_to_audit_security(self, invoke):
        # Arrange
        args = ["audit", "--help"]
        # Act
        result = invoke(args)
        # Assert
        assert "audit-security [OPTIONS] [PATH]" in result.stdout

    def test_tex_alias_forwards_options(self, invoke, tmp_path):
        # Arrange
        tex = tmp_path / "eq.tex"
        tex.write_text("$x$")
        # Act
        result = invoke(["tex", "to-vec", str(tex), "--format", "pdf", "--dry-run"])
        # Assert
        assert str(tmp_path / "eq.pdf") in result.stdout

    def test_mcp_alias_forwards_json(self, invoke):
        # Arrange
        args = ["mcp", "installation", "--json"]
        # Act
        result = invoke(args)
        # Assert
        assert _stdout_json(result)["mcpServers"]["scitex"]["args"] == [
            "mcp",
            "start",
        ]



# EOF
