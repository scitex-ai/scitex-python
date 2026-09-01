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


# EOF
