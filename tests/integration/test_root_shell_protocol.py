"""Standard completion bootstrap uses shared callbacks and owned filesystem state."""

import re

import pytest
from click.testing import CliRunner

from scitex.cli.main import cli


@pytest.fixture
def owned_shell(tmp_path, monkeypatch):
    home = tmp_path / "home"
    home.mkdir()
    state = tmp_path / "state"
    runtime = tmp_path / "runtime"
    runtime.mkdir()
    monkeypatch.setenv("HOME", str(home))
    monkeypatch.setenv("SCITEX_DIR", str(state))
    monkeypatch.setenv("XDG_RUNTIME_DIR", str(runtime))
    monkeypatch.setenv("COVERAGE_FILE", str(tmp_path / ".coverage"))
    return home, state


def test_standard_print_command_generates_actual_bash_completion(owned_shell):
    # Arrange
    runner = CliRunner()
    # Act
    result = runner.invoke(cli, ["print-shell-completion", "--shell", "bash"])
    # Assert
    assert (result.exit_code, "_SCITEX_COMPLETE=bash_complete" in result.stdout) == (
        0,
        True,
    )


def test_standard_install_preview_preserves_owned_shell_state(owned_shell):
    # Arrange
    home, state = owned_shell
    rc = home / ".bashrc"
    original = "export KEEP_ME=1\n"
    rc.write_text(original)
    # Act
    result = CliRunner().invoke(
        cli, ["install-shell-completion", "--shell", "bash", "--dry-run", "--yes"]
    )
    # Assert
    assert (result.exit_code, rc.read_text(), state.exists()) == (0, original, False)


def test_standard_install_preserves_existing_settings_and_is_idempotent(owned_shell):
    # Arrange
    home, state = owned_shell
    rc = home / ".bashrc"
    original = "export KEEP_ME=1\n"
    rc.write_text(original)
    runner = CliRunner()
    args = ["install-shell-completion", "--shell", "bash", "--yes"]
    # Act
    first = runner.invoke(cli, args)
    installed = rc.read_text()
    second = runner.invoke(cli, args)
    cache = state / "scitex" / "runtime" / "completion" / "scitex"
    symlink = home / ".local/share/bash-completion/completions/scitex"
    # Assert
    assert (
        first.exit_code,
        second.exit_code,
        installed.startswith(original),
        rc.read_text() == installed,
        cache.is_file(),
        symlink.is_symlink() and symlink.resolve() == cache,
    ) == (0, 0, True, True, True, True)


def test_protocol_setup_does_not_replace_developer_completion_or_expand_main_help(
    owned_shell,
):
    # Arrange
    runner = CliRunner()
    # Act
    old_group = runner.invoke(cli, ["completion", "--help"])
    help_result = runner.invoke(cli, ["--help"])
    listed = re.findall(r"^  ([a-z][a-z0-9-]*)\s{2,}\S", help_result.stdout, re.M)
    # Assert
    assert (
        old_group.exit_code,
        "status" in old_group.stdout,
        help_result.exit_code,
        bool(set(listed) & {"install-shell-completion", "print-shell-completion"}),
    ) == (0, True, 0, False)
