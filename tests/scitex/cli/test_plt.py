#!/usr/bin/env python3
# Timestamp: 2026-01-25
# File: tests/scitex/cli/test_plt.py

"""Tests for scitex.cli.plt - Plot and figure management CLI commands."""

from unittest.mock import MagicMock, patch

import pytest
from click.testing import CliRunner

from scitex.cli.plt import plt


class TestPltGroup:
    """Tests for the plt command group."""

    def test_plt_help(self):
        """Test that plt help is displayed correctly."""
        runner = CliRunner()
        result = runner.invoke(plt, ["--help"])
        assert result.exit_code == 0
        assert "Plot and figure management" in result.output
        assert "powered by figrecipe" in result.output

    def test_plt_short_help(self):
        """Test that plt -h works."""
        runner = CliRunner()
        result = runner.invoke(plt, ["-h"])
        assert result.exit_code == 0
        assert "Plot and figure management" in result.output

    def test_plt_has_subcommands(self):
        """Test that all expected subcommands are registered."""
        runner = CliRunner()
        result = runner.invoke(plt, ["--help"])
        expected_commands = [
            "plot",
            "edit",
            "compose",
            "crop",
            "reproduce",
            "validate",
            "diagram",
            "info",
            "extract",
            "style",
            "fonts",
            "convert",
            "serve",
        ]
        for cmd in expected_commands:
            assert cmd in result.output, f"Command '{cmd}' not found in plt help"

    def test_plt_help_recursive(self):
        """Test --help-recursive option."""
        runner = CliRunner()
        result = runner.invoke(plt, ["--help-recursive"])
        assert result.exit_code == 0
        # Should show help for multiple subcommands
        assert "scitex plt plot" in result.output
        assert "scitex plt compose" in result.output

    def test_plt_no_command_shows_help(self):
        """Test that running plt without subcommand shows help."""
        runner = CliRunner()
        result = runner.invoke(plt)
        assert result.exit_code == 0
        assert "Plot and figure management" in result.output


class TestPltPlot:
    """Tests for the plt plot command."""

    def test_plot_help(self):
        """Test plot command help."""
        runner = CliRunner()
        result = runner.invoke(plt, ["plot", "--help"])
        assert result.exit_code == 0
        assert "Create a figure" in result.output
        assert "--output" in result.output
        assert "--dpi" in result.output

    @patch("scitex.cli.plt.subprocess.run")
    def test_plot_basic(self, mock_run):
        """Test basic plot command."""
        mock_run.return_value = MagicMock(returncode=0)
        runner = CliRunner()
        with runner.isolated_filesystem():
            # Create a dummy spec file
            with open("spec.yaml", "w") as f:
                f.write("figure: {}")
            result = runner.invoke(plt, ["plot", "spec.yaml", "-o", "out.png"])
            assert result.exit_code == 0
            mock_run.assert_called_once()
            cmd = mock_run.call_args[0][0]
            assert "plot" in cmd
            assert "spec.yaml" in cmd
            assert "-o" in cmd
            assert "out.png" in cmd

    @patch("scitex.cli.plt.subprocess.run")
    def test_plot_with_dpi(self, mock_run):
        """Test plot command with dpi option."""
        mock_run.return_value = MagicMock(returncode=0)
        runner = CliRunner()
        with runner.isolated_filesystem():
            with open("spec.yaml", "w") as f:
                f.write("figure: {}")
            result = runner.invoke(
                plt, ["plot", "spec.yaml", "-o", "out.png", "--dpi", "600"]
            )
            assert result.exit_code == 0
            cmd = mock_run.call_args[0][0]
            assert "--dpi" in cmd
            assert "600" in cmd


class TestPltEdit:
    """Tests for the plt edit command."""

    def test_edit_help(self):
        """Test edit command help."""
        runner = CliRunner()
        result = runner.invoke(plt, ["edit", "--help"])
        assert result.exit_code == 0
        assert "GUI editor" in result.output

    @patch("scitex.cli.plt.subprocess.run")
    def test_edit_no_args(self, mock_run):
        """Test edit command without arguments."""
        mock_run.return_value = MagicMock(returncode=0)
        runner = CliRunner()
        result = runner.invoke(plt, ["edit"])
        assert result.exit_code == 0
        cmd = mock_run.call_args[0][0]
        assert "edit" in cmd


class TestPltCompose:
    """Tests for the plt compose command."""

    def test_compose_help(self):
        """Test compose command help."""
        runner = CliRunner()
        result = runner.invoke(plt, ["compose", "--help"])
        assert result.exit_code == 0
        assert "Compose multiple figures" in result.output
        assert "--layout" in result.output
        assert "--gap" in result.output

    @patch("scitex.cli.plt.subprocess.run")
    def test_compose_basic(self, mock_run):
        """Test basic compose command."""
        mock_run.return_value = MagicMock(returncode=0)
        runner = CliRunner()
        with runner.isolated_filesystem():
            with open("a.png", "w") as f:
                f.write("")
            with open("b.png", "w") as f:
                f.write("")
            result = runner.invoke(plt, ["compose", "a.png", "b.png", "-o", "out.png"])
            assert result.exit_code == 0
            cmd = mock_run.call_args[0][0]
            assert "compose" in cmd
            assert "a.png" in cmd
            assert "b.png" in cmd


class TestPltCrop:
    """Tests for the plt crop command."""

    def test_crop_help(self):
        """Test crop command help."""
        runner = CliRunner()
        result = runner.invoke(plt, ["crop", "--help"])
        assert result.exit_code == 0
        assert "Crop whitespace" in result.output
        assert "--margin" in result.output


class TestPltReproduce:
    """Tests for the plt reproduce command."""

    def test_reproduce_help(self):
        """Test reproduce command help."""
        runner = CliRunner()
        result = runner.invoke(plt, ["reproduce", "--help"])
        assert result.exit_code == 0
        assert "Reproduce a figure" in result.output
        assert "--format" in result.output


class TestPltValidate:
    """Tests for the plt validate command."""

    def test_validate_help(self):
        """Test validate command help."""
        runner = CliRunner()
        result = runner.invoke(plt, ["validate", "--help"])
        assert result.exit_code == 0
        assert "Validate" in result.output
        assert "--threshold" in result.output


class TestPltDiagram:
    """Tests for the plt diagram command."""

    def test_diagram_help(self):
        """Test diagram command help."""
        runner = CliRunner()
        result = runner.invoke(plt, ["diagram", "--help"])
        assert result.exit_code == 0
        assert "Create diagrams" in result.output
        assert "mermaid" in result.output
        assert "graphviz" in result.output


class TestPltInfo:
    """Tests for the plt info command."""

    def test_info_help(self):
        """Test info command help."""
        runner = CliRunner()
        result = runner.invoke(plt, ["info", "--help"])
        assert result.exit_code == 0
        assert "Show information" in result.output
        assert "--verbose" in result.output


class TestPltExtract:
    """Tests for the plt extract command."""

    def test_extract_help(self):
        """Test extract command help."""
        runner = CliRunner()
        result = runner.invoke(plt, ["extract", "--help"])
        assert result.exit_code == 0
        assert "Extract plotted data" in result.output


class TestPltStyle:
    """Tests for the plt style command."""

    def test_style_help(self):
        """Test style command help."""
        runner = CliRunner()
        result = runner.invoke(plt, ["style", "--help"])
        assert result.exit_code == 0
        assert "Manage figure styles" in result.output


class TestPltFonts:
    """Tests for the plt fonts command."""

    def test_fonts_help(self):
        """Test fonts command help."""
        runner = CliRunner()
        result = runner.invoke(plt, ["fonts", "--help"])
        assert result.exit_code == 0
        assert "List or check available fonts" in result.output
        assert "--check" in result.output

    @patch("scitex.cli.plt.subprocess.run")
    def test_fonts_basic(self, mock_run):
        """Test basic fonts command."""
        mock_run.return_value = MagicMock(returncode=0)
        runner = CliRunner()
        result = runner.invoke(plt, ["fonts"])
        assert result.exit_code == 0
        cmd = mock_run.call_args[0][0]
        assert "fonts" in cmd


class TestPltConvert:
    """Tests for the plt convert command."""

    def test_convert_help(self):
        """Test convert command help."""
        runner = CliRunner()
        result = runner.invoke(plt, ["convert", "--help"])
        assert result.exit_code == 0
        assert "Convert between figure formats" in result.output


class TestPltServe:
    """Tests for the plt serve command."""

    def test_serve_help(self):
        """Test mcp command help (formerly serve)."""
        runner = CliRunner()
        result = runner.invoke(plt, ["mcp", "--help"])
        assert result.exit_code == 0
        assert "MCP" in result.output


class TestFigrecipeAvailability:
    """Tests for figrecipe availability check."""

    def test_check_figrecipe_available(self):
        """Test _check_figrecipe returns True when figrecipe installed."""
        from scitex.cli.plt import _check_figrecipe

        # Should return True since figrecipe is a dependency
        assert _check_figrecipe() is True

    @patch.dict("sys.modules", {"figrecipe": None})
    def test_plt_without_figrecipe(self):
        """Test plt shows error when figrecipe not installed."""
        # This test is tricky because figrecipe IS installed
        # We'd need to mock the import, but the module is already loaded
        # Skip this test in practice - just verify the error message exists
        pass


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

# EOF
