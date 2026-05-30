#!/usr/bin/env python3
# File: ./tests/scitex/test___main__.py

"""Tests for the slim scitex.__main__ CLI entry point.

The entry point was slimmed: ``main()`` checks CLI dependencies then
delegates to ``scitex.cli.main:cli`` (Click). The legacy
``print_config_main`` dispatch no longer exists. These tests assert the
current thin contract — a dependency check + Click delegation — against the
real module and a real subprocess, with no mocks (per the ecosystem
no-mock policy).
"""

import subprocess
import sys

import pytest


class TestSciTeXMainStructure:
    """Structural contract of the slim entry point."""

    def test_main_function_exists(self):
        # Arrange
        import scitex.__main__ as main_module

        # Act
        has_main = hasattr(main_module, "main")
        # Assert
        assert has_main

    def test_main_function_is_callable(self):
        # Arrange
        import scitex.__main__ as main_module

        # Act
        is_callable = callable(main_module.main)
        # Assert
        assert is_callable

    def test_dependency_check_helper_exists(self):
        # Arrange
        import scitex.__main__ as main_module

        # Act
        has_helper = hasattr(main_module, "_check_cli_dependencies")
        # Assert
        assert has_helper

    def test_sys_module_is_imported(self):
        # Arrange
        import scitex.__main__ as main_module

        # Act
        has_sys = hasattr(main_module, "sys")
        # Assert
        assert has_sys

    def test_print_config_main_is_gone(self):
        # The legacy print_config dispatch was removed when the entry point
        # was slimmed to a Click delegate.
        # Arrange
        import scitex.__main__ as main_module

        # Act
        has_legacy = hasattr(main_module, "print_config_main")
        # Assert
        assert not has_legacy


class TestSciTeXMainDependencyCheck:
    """Behavior of the CLI-dependency gate against the real environment."""

    def test_returns_empty_list_when_click_available(self):
        # click is a real test-env dependency, so the gate reports nothing
        # missing.
        # Arrange
        import scitex.__main__ as main_module

        # Act
        missing = main_module._check_cli_dependencies()
        # Assert
        assert missing == []

    def test_returns_a_list(self):
        # Arrange
        import scitex.__main__ as main_module

        # Act
        missing = main_module._check_cli_dependencies()
        # Assert
        assert isinstance(missing, list)


class TestSciTeXMainDelegation:
    """main() delegates to the real Click CLI via `python -m scitex`."""

    def test_help_subprocess_exits_zero(self):
        # Arrange
        cmd = [sys.executable, "-m", "scitex", "--help"]
        # Act
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
        # Assert
        assert result.returncode == 0

    def test_help_subprocess_prints_click_usage(self):
        # Arrange
        cmd = [sys.executable, "-m", "scitex", "--help"]
        # Act
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
        # Assert
        assert "Usage: python -m scitex" in result.stdout

    def test_unknown_command_subprocess_exits_nonzero(self):
        # Click reports an error and exits non-zero for an unknown command —
        # this is the real delegation surface (no print_config dispatch).
        # Arrange
        cmd = [sys.executable, "-m", "scitex", "definitely-not-a-command"]
        # Act
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
        # Assert
        assert result.returncode != 0


class TestSciTeXMainDocumentation:
    """Documentation contract of the slim entry point."""

    def test_module_has_a_docstring(self):
        # Arrange
        import scitex.__main__ as main_module

        # Act
        doc = main_module.__doc__
        # Assert
        assert doc is not None

    def test_module_docstring_mentions_entry_point(self):
        # Arrange
        import scitex.__main__ as main_module

        # Act
        doc = (main_module.__doc__ or "").lower()
        # Assert
        assert "entry point" in doc

    def test_main_function_has_a_docstring(self):
        # Arrange
        import scitex.__main__ as main_module

        # Act
        doc = main_module.main.__doc__
        # Assert
        assert doc is not None


if __name__ == "__main__":
    import os

    pytest.main([os.path.abspath(__file__)])
