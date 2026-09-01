#!/usr/bin/env python3
# File: ./tests/scitex/cli/test_completion.py

"""Tests for the canonical ``completion`` noun group (doctrine §1b).

Contract (CLI-standardization slice 5, operator-confirmed 2026-07-07):
- ``completion`` is a GROUP (bare invocation shows help; never installs),
- verbs: ``install [--shell] [--dry-run]`` and ``status``,
- ``install --dry-run`` prints the target rc file + script, writes nothing,
- the old ``bash``/``zsh``/``fish`` script-dump leaves are hidden
  warn-phase deprecated aliases.

No mocks: runs the real click app via CliRunner; PATH-dependent cases
skip when the ``scitex`` binary is unavailable.
"""

import os
import re
import shutil

import pytest
from click.testing import CliRunner

from scitex.cli.completion import completion

_SCITEX_ON_PATH = shutil.which("scitex") is not None


def _all_output(result) -> str:
    """stdout + stderr regardless of the CliRunner mix_stderr era."""
    out = result.output
    try:
        out += result.stderr
    except (ValueError, AttributeError):
        pass
    return out


def _bashrc_content() -> str | None:
    path = os.path.expanduser("~/.bashrc")
    if not os.path.exists(path):
        return None
    with open(path) as f:
        return f.read()


@pytest.fixture(scope="module")
def group_help_result():
    return CliRunner().invoke(completion, ["--help"])


class TestCompletionGroupHelp:
    """The group lists its verbs and hides the deprecated leaves."""

    def test_group_help_exits_zero(self, group_help_result):
        # Arrange
        result = group_help_result
        # Act
        exit_code = result.exit_code
        # Assert
        assert exit_code == 0

    @pytest.mark.parametrize("verb", ["install", "status"])
    def test_group_help_lists_canonical_verb(self, group_help_result, verb):
        # Arrange
        output = group_help_result.output
        # Act
        listed = re.search(rf"^  {verb}\s", output, re.M)
        # Assert
        assert listed is not None

    @pytest.mark.parametrize("leaf", ["bash", "zsh", "fish"])
    def test_group_help_hides_deprecated_script_leaf(self, group_help_result, leaf):
        # Arrange
        output = group_help_result.output
        # Act
        listed = re.search(rf"^  {leaf}\s", output, re.M)
        # Assert
        assert listed is None

    def test_bare_group_invocation_shows_help_not_install(self):
        # Arrange
        runner = CliRunner()
        rc_before = _bashrc_content()
        # Act
        result = runner.invoke(completion, [])
        rc_after = _bashrc_content()
        # Assert
        assert ("install" in result.output) and (rc_before == rc_after)


class TestCompletionInstallDryRun:
    """--dry-run prints the plan and never touches the filesystem."""

    @pytest.mark.skipif(not _SCITEX_ON_PATH, reason="scitex binary not on PATH")
    def test_dry_run_exits_zero(self):
        # Arrange
        runner = CliRunner()
        # Act
        result = runner.invoke(completion, ["install", "--dry-run", "--shell", "bash"])
        # Assert
        assert result.exit_code == 0

    @pytest.mark.skipif(not _SCITEX_ON_PATH, reason="scitex binary not on PATH")
    def test_dry_run_prints_target_rc_file(self):
        # Arrange
        runner = CliRunner()
        # Act
        result = runner.invoke(completion, ["install", "--dry-run", "--shell", "bash"])
        # Assert
        assert "# would append to:" in result.output

    @pytest.mark.skipif(not _SCITEX_ON_PATH, reason="scitex binary not on PATH")
    def test_dry_run_prints_the_completion_script(self):
        # Arrange
        runner = CliRunner()
        # Act
        result = runner.invoke(completion, ["install", "--dry-run", "--shell", "bash"])
        # Assert
        assert "_SCITEX_COMPLETE=bash_source" in result.output

    @pytest.mark.skipif(not _SCITEX_ON_PATH, reason="scitex binary not on PATH")
    def test_dry_run_does_not_modify_the_rc_file(self):
        # Arrange
        runner = CliRunner()
        rc_before = _bashrc_content()
        # Act
        runner.invoke(completion, ["install", "--dry-run", "--shell", "bash"])
        rc_after = _bashrc_content()
        # Assert
        assert rc_before == rc_after


class TestCompletionStatus:
    """`completion status` reports without side effects."""

    def test_status_exits_zero(self):
        # Arrange
        runner = CliRunner()
        # Act
        result = runner.invoke(completion, ["status"])
        # Assert
        assert result.exit_code == 0

    def test_status_prints_the_report_header(self):
        # Arrange
        runner = CliRunner()
        # Act
        result = runner.invoke(completion, ["status"])
        # Assert
        assert "Shell Completion Status" in result.output


class TestDeprecatedScriptLeaves:
    """Old bash/zsh/fish leaves still work but warn (warn-phase)."""

    @pytest.mark.skipif(not _SCITEX_ON_PATH, reason="scitex binary not on PATH")
    def test_bash_leaf_still_prints_the_script(self):
        # Arrange
        runner = CliRunner()
        # Act
        result = runner.invoke(completion, ["bash"])
        # Assert
        assert "_SCITEX_COMPLETE=bash_source" in result.output

    @pytest.mark.skipif(not _SCITEX_ON_PATH, reason="scitex binary not on PATH")
    def test_bash_leaf_warns_about_deprecation(self):
        # Arrange
        runner = CliRunner()
        # Act
        result = runner.invoke(completion, ["bash"])
        # Assert
        assert "deprecated" in _all_output(result)

    @pytest.mark.skipif(not _SCITEX_ON_PATH, reason="scitex binary not on PATH")
    def test_bash_leaf_exits_zero(self):
        # Arrange
        runner = CliRunner()
        # Act
        result = runner.invoke(completion, ["bash"])
        # Assert
        assert result.exit_code == 0


# EOF
