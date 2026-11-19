#!/usr/bin/env python3
# File: ./tests/scitex/cli/test_cli_convention.py

"""Umbrella CLI standardization (noun/verb convention, 2026-11-19).

Covers:
- renamed commands are mounted under their canonical names,
- every old name is a hidden alias that still works and prints a one-line
  deprecation note to stderr,
- the new flags: ``--json`` prints valid JSON, ``--dry-run`` changes
  nothing on disk, ``--yes`` lets a command run without any prompt,
- the root help shows the version and the config-path fallback, and the
  canonical shell-completion leaves exist.

No mocks: every case runs the real click app through CliRunner, and
environment variables are set with CliRunner's own ``env=``. The
deprecation note is printed once per shell session (scitex-dev keys a
marker file on the parent PID under $XDG_RUNTIME_DIR), so each test gets
its own XDG_RUNTIME_DIR.
"""

import json
import zipfile

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


def _tree(path):
    return sorted(p.relative_to(path) for p in path.rglob("*"))


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


# --------------------------------------------------------------------------- #
# --json prints valid JSON                                                     #
# --------------------------------------------------------------------------- #


class TestJsonFlag:
    @pytest.mark.parametrize(
        "args,expected_key",
        [
            (["repro", "get-timestamp", "--json"], "timestamp"),
            (["audit-tool", "status", "--json"], "pip-audit"),
            (["mcp", "show-installation", "--json"], "mcpServers"),
            (["config", "show", "logs", "--json"], "path"),
            (["completion", "status", "--json"], "installed"),
            (["browser", "show", "--json"], "instruction"),
            (["browser", "hide", "--json"], "instruction"),
        ],
        ids=lambda v: " ".join(v) if isinstance(v, list) else str(v),
    )
    def test_json_object_has_its_key(self, invoke, args, expected_key):
        # Arrange
        key = expected_key
        # Act
        payload = _stdout_json(invoke(args))
        # Assert
        assert key in payload

    def test_repro_get_id_json_is_a_list_of_ids(self, invoke):
        # Arrange
        args = ["repro", "get-id", "--count", "2", "--json"]
        # Act
        payload = _stdout_json(invoke(args))
        # Assert
        assert len(payload) == 2

    def test_browser_list_json_is_an_object(self, invoke, tmp_path):
        # Arrange
        env = {"HOME": str(tmp_path)}
        # Act
        payload = _stdout_json(invoke(["browser", "list", "--json"], env=env))
        # Assert
        assert payload == {}

    def test_skills_install_dry_run_json_names_the_destination(self, invoke, tmp_path):
        # Arrange
        args = ["skills", "install", "--package", "scitex-dev", "--dest", str(tmp_path)]
        # Act
        payload = _stdout_json(invoke([*args, "--dry-run", "--json"]))
        # Assert
        assert payload["dest"] == str(tmp_path)

    def test_event_list_json_is_an_array(self, invoke):
        pytest.importorskip("scitex_events")
        # Arrange
        args = ["event", "list", "--limit", "1", "--json"]
        # Act
        payload = _stdout_json(invoke(args))
        # Assert
        assert isinstance(payload, list)


# --------------------------------------------------------------------------- #
# --dry-run changes nothing                                                    #
# --------------------------------------------------------------------------- #


class TestDryRunFlag:
    def test_tex_compile_dry_run_writes_nothing(self, invoke, tmp_path):
        # Arrange
        tex = tmp_path / "paper.tex"
        tex.write_text("\\documentclass{article}\\begin{document}x\\end{document}")
        before = _tree(tmp_path)
        # Act
        invoke(["tex", "compile", str(tex), "--dry-run"])
        # Assert
        assert _tree(tmp_path) == before

    def test_tex_convert_to_vector_dry_run_writes_nothing(self, invoke, tmp_path):
        # Arrange
        tex = tmp_path / "eq.tex"
        tex.write_text("$x$")
        before = _tree(tmp_path)
        # Act
        invoke(["tex", "convert-to-vector", str(tex), "--dry-run"])
        # Assert
        assert _tree(tmp_path) == before

    def test_bundle_convert_dry_run_writes_nothing(self, invoke, tmp_path):
        # Arrange
        figz = tmp_path / "fig.figz"
        with zipfile.ZipFile(figz, "w") as zf:
            zf.writestr("spec.json", json.dumps({"kind": "figure"}))
        before = _tree(tmp_path)
        # Act
        invoke(["bundle", "convert", str(figz), "--dry-run"])
        # Assert
        assert _tree(tmp_path) == before

    def test_browser_save_as_pdf_dry_run_writes_nothing(self, invoke, tmp_path):
        # Arrange
        out = tmp_path / "o.pdf"
        # Act
        invoke(["browser", "save-as-pdf", "https://example.com", str(out), "--dry-run"])
        # Assert
        assert _tree(tmp_path) == []

    def test_skills_install_dry_run_writes_nothing(self, invoke, tmp_path):
        # Arrange
        args = ["skills", "install", "--package", "scitex-dev", "--dest", str(tmp_path)]
        # Act
        invoke([*args, "--dry-run"])
        # Assert
        assert _tree(tmp_path) == []

    def test_config_init_dry_run_creates_no_directory(self, invoke, tmp_path):
        # Arrange
        env = {"SCITEX_DIR": str(tmp_path / "scitex")}
        # Act
        invoke(["config", "init", "--dry-run"], env=env)
        # Assert
        assert _tree(tmp_path) == []

    def test_install_shell_completion_dry_run_leaves_home_untouched(
        self, invoke, tmp_path
    ):
        # Arrange
        env = {"HOME": str(tmp_path), "SCITEX_DIR": str(tmp_path / ".scitex")}
        # Act
        invoke(["install-shell-completion", "--shell", "bash", "--dry-run"], env=env)
        # Assert
        assert _tree(tmp_path) == []

    def test_mcp_start_dry_run_returns_without_serving(self, invoke):
        # Arrange
        args = ["mcp", "start", "--transport", "http", "--port", "1", "--dry-run"]
        # Act
        result = invoke(args)
        # Assert
        assert result.exit_code == 0 and "[dry-run]" in result.stdout


class TestBundleConvert:
    """`bundle convert` writes a .stx (the helper used to crash on every call)."""

    def test_convert_writes_stx_with_a_bundle_id(self, invoke, tmp_path):
        # Arrange
        figz = tmp_path / "fig.figz"
        with zipfile.ZipFile(figz, "w") as zf:
            zf.writestr("spec.json", json.dumps({"kind": "figure"}))
        # Act
        invoke(["bundle", "convert", str(figz)])
        # Assert
        with zipfile.ZipFile(tmp_path / "fig.stx") as zf:
            assert json.loads(zf.read("spec.json"))["bundle_id"]


# --------------------------------------------------------------------------- #
# --yes runs without any prompt (stdin is empty; a prompt would abort)         #
# --------------------------------------------------------------------------- #


class TestYesFlag:
    def test_config_init_yes_completes_without_input(self, invoke, tmp_path):
        # Arrange
        env = {"SCITEX_DIR": str(tmp_path / "scitex")}
        # Act
        result = invoke(["config", "init", "--yes"], input="", env=env)
        # Assert
        assert result.exit_code == 0 and (tmp_path / "scitex").is_dir()

    def test_skills_install_yes_installs_without_input(self, invoke, tmp_path):
        # Arrange
        args = ["skills", "install", "--package", "scitex-dev", "--dest", str(tmp_path)]
        # Act
        result = invoke([*args, "--yes"], input="")
        # Assert
        assert result.exit_code == 0 and _tree(tmp_path)

    @pytest.mark.parametrize(
        "args",
        [
            ["audit-tool", "install", "--dry-run", "-y"],
            ["mcp", "start", "--dry-run", "--yes"],
            ["template", "clone", "minimal", "./x", "--dry-run", "--yes"],
            ["install-shell-completion", "--dry-run", "--yes"],
        ],
        ids=lambda a: " ".join(a),
    )
    def test_yes_is_accepted_and_exits_zero_without_input(self, invoke, args):
        # Arrange
        stdin = ""
        # Act
        result = invoke(args, input=stdin)
        # Assert
        assert result.exit_code == 0


# --------------------------------------------------------------------------- #
# Root help and shell completion                                               #
# --------------------------------------------------------------------------- #


class TestRootHelp:
    def test_root_help_opens_with_the_version(self, invoke):
        # Arrange
        from scitex.__version__ import __version__

        # Act
        result = invoke(["--help"])
        # Assert
        assert f"scitex (v{__version__})" in result.stdout

    def test_root_help_documents_config_location(self, invoke):
        # Arrange
        args = ["--help"]
        # Act
        result = invoke(args)
        # Assert
        assert "~/.scitex/" in result.stdout

    def test_print_shell_completion_prints_a_script(self, invoke):
        # Arrange
        args = ["print-shell-completion", "--shell", "bash"]
        # Act
        result = invoke(args)
        # Assert
        assert "_SCITEX_COMPLETE" in result.stdout

    def test_completion_group_still_installs(self, invoke, tmp_path):
        # Arrange
        env = {"HOME": str(tmp_path)}
        # Act
        result = invoke(
            ["completion", "install", "--shell", "bash", "--dry-run"], env=env
        )
        # Assert
        assert result.exit_code == 0


# EOF
