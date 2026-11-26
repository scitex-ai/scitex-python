#!/usr/bin/env python3
# File: ./tests/scitex/cli/test_main.py

"""Tests for the umbrella root CLI (CLI-standardization slice 5).

Covers:
- ``-V`` short flag for ``--version``,
- categorized root help (doctrine §4a fixed ordered headers),
- retired duplicate namespaces hidden from help,
- warn-phase alias behavior with/without scitex-dev's click_compat,
- writer/scholar mount smoke (--help exits 0).

No mocks (ecosystem no-mock policy): everything runs against the real
click app via CliRunner.
"""

import importlib.util
import re

import pytest
from click.testing import CliRunner

from scitex.cli.main import cli

_HAS_CLICK_COMPAT = bool(
    importlib.util.find_spec("scitex_dev")
    and importlib.util.find_spec("scitex_dev._ecosystem.click_compat")
)


def _all_output(result) -> str:
    """stdout + stderr regardless of the CliRunner mix_stderr era."""
    out = result.output
    try:
        out += result.stderr
    except (ValueError, AttributeError):
        pass
    return out


@pytest.fixture(scope="module")
def version_result():
    return CliRunner().invoke(cli, ["-V"])


@pytest.fixture(scope="module")
def help_result():
    return CliRunner().invoke(cli, ["--help"])


class TestVersionShortFlag:
    """`scitex -V` behaves like `scitex --version`."""

    def test_dash_v_exits_zero(self, version_result):
        # Arrange
        result = version_result
        # Act
        exit_code = result.exit_code
        # Assert
        assert exit_code == 0

    def test_dash_v_prints_a_version_string(self, version_result):
        # Arrange
        result = version_result
        # Act
        output = result.output
        # Assert
        assert "version" in output


class TestCategorizedRootHelp:
    """Root help renders the §4a fixed ordered category headers."""

    def test_root_help_exits_zero(self, help_result):
        # Arrange
        result = help_result
        # Act
        exit_code = result.exit_code
        # Assert
        assert exit_code == 0

    @pytest.mark.parametrize(
        "header", ["Core:", "Service:", "Diagnostics:", "Introspection:", "Shell:"]
    )
    def test_root_help_renders_category_header(self, help_result, header):
        # Arrange
        output = help_result.output
        # Act
        present = header in output
        # Assert
        assert present

    def test_core_header_renders_before_shell_header(self, help_result):
        # Arrange
        output = help_result.output
        # Act
        core_first = output.index("Core:") < output.index("Shell:")
        # Assert
        assert core_first

    def test_other_category_never_renders(self, help_result):
        # Arrange
        output = help_result.output
        # Act
        present = "Other:" in output
        # Assert
        assert not present

    @pytest.mark.parametrize("retired", ["notify", "verify", "events", "socialia"])
    def test_retired_duplicate_is_hidden_from_help(self, help_result, retired):
        # Arrange
        output = help_result.output
        # Act
        listed = re.search(rf"^  {retired}\s", output, re.M)
        # Assert
        assert listed is None


class TestDeprecatedAliasBehavior:
    """Warn-phase aliases forward when click_compat is importable."""

    @pytest.mark.skipif(
        not _HAS_CLICK_COMPAT, reason="scitex-dev click_compat not installed"
    )
    def test_notify_alias_help_page_marks_deprecation(self):
        # Arrange
        runner = CliRunner()
        # Act
        result = runner.invoke(cli, ["notify", "--help"])
        # Assert
        assert "(deprecated)" in result.output

    @pytest.mark.skipif(
        not _HAS_CLICK_COMPAT, reason="scitex-dev click_compat not installed"
    )
    def test_notify_alias_help_exits_zero(self):
        # Arrange
        runner = CliRunner()
        # Act
        result = runner.invoke(cli, ["notify", "--help"])
        # Assert
        assert result.exit_code == 0

    @pytest.mark.skipif(
        _HAS_CLICK_COMPAT, reason="click_compat present: alias exists instead"
    )
    def test_notify_without_click_compat_is_unknown_command(self):
        # Arrange
        runner = CliRunner()
        # Act
        result = runner.invoke(cli, ["notify"])
        # Assert
        assert result.exit_code != 0


class TestPeerMountSmoke:
    """Re-exported peer groups respond to --help (mount regression guard)."""

    def test_writer_help_exits_zero(self):
        pytest.importorskip("scitex_writer")
        # Arrange
        runner = CliRunner()
        # Act
        result = runner.invoke(cli, ["writer", "--help"])
        # Assert
        assert result.exit_code == 0

    def test_scholar_help_exits_zero(self):
        pytest.importorskip("scitex_scholar")
        # Arrange
        runner = CliRunner()
        # Act
        result = runner.invoke(cli, ["scholar", "--help"])
        # Assert
        assert result.exit_code == 0

    def test_writer_help_renders_the_standalone_group_usage(self):
        pytest.importorskip("scitex_writer")
        # Arrange
        runner = CliRunner()
        # Act
        result = runner.invoke(cli, ["writer", "--help"])
        # Assert
        assert "Usage:" in result.output


class TestLazyGroupUnresolvableSubcommand:
    """A lazy subcommand whose module cannot be imported resolves to None.

    The failure is recorded as a scitex-logging debug record (PS-220);
    nothing is raised and nothing is written to stdout.
    """

    @staticmethod
    def _group():
        from scitex.cli.main import LazyGroup

        return LazyGroup(
            name="probe",
            lazy_subcommands={
                "ghost": ("scitex_no_such_module_for_lazy_probe", "cli", "ghost"),
            },
        )

    def test_get_command_returns_none(self):
        # Arrange
        group = self._group()
        # Act
        cmd = group.get_command(None, "ghost")
        # Assert
        assert cmd is None

    def test_get_command_writes_nothing_to_stdout(self, capsys):
        # Arrange
        group = self._group()
        # Act
        group.get_command(None, "ghost")
        captured = capsys.readouterr()
        # Assert
        assert captured.out == ""


# =========================================================================== #
# CLI standardization (2026-11-19): --json / --dry-run / --yes and root help  #
# =========================================================================== #
# Environment variables are set with CliRunner's own ``env=``; each test gets
# its own $XDG_RUNTIME_DIR so scitex-dev's once-per-shell alias note fires.

import json as _json
import zipfile as _zipfile


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
    return _json.loads(result.stdout)


def _tree(path):
    return sorted(p.relative_to(path) for p in path.rglob("*"))


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
        with _zipfile.ZipFile(figz, "w") as zf:
            zf.writestr("spec.json", _json.dumps({"kind": "figure"}))
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
        with _zipfile.ZipFile(figz, "w") as zf:
            zf.writestr("spec.json", _json.dumps({"kind": "figure"}))
        # Act
        invoke(["bundle", "convert", str(figz)])
        # Assert
        with _zipfile.ZipFile(tmp_path / "fig.stx") as zf:
            assert _json.loads(zf.read("spec.json"))["bundle_id"]


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
