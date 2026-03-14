#!/usr/bin/env python3
"""Tests for scitex.cli.main - Main CLI entry point."""

import os
import sys
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from click.testing import CliRunner

from scitex.cli.main import cli, completion


class TestCLIGroup:
    """Tests for the main CLI command group."""

    def test_cli_help(self):
        """Test that CLI help is displayed correctly."""
        runner = CliRunner()
        result = runner.invoke(cli, ["--help"])
        assert result.exit_code == 0
        assert "Integrated Scientific Research Platform" in result.output

    def test_cli_short_help(self):
        """Test that -h also shows help."""
        runner = CliRunner()
        result = runner.invoke(cli, ["-h"])
        assert result.exit_code == 0
        assert "SciTeX" in result.output

    def test_cli_version(self):
        """Test that version option works."""
        runner = CliRunner()
        result = runner.invoke(cli, ["--version"])
        # Exit code 0 for version display
        assert result.exit_code == 0

    def test_cli_has_subcommands(self):
        """Test that all expected subcommands are registered."""
        runner = CliRunner()
        result = runner.invoke(cli, ["--help"])
        expected_commands = [
            "cloud",
            "config",
            "convert",
            "scholar",
            "security",
            "web",
            "writer",
            "completion",
        ]
        for cmd in expected_commands:
            assert cmd in result.output, f"Command '{cmd}' not found in CLI help"

    def test_cli_unknown_command(self):
        """Test that unknown command shows error."""
        runner = CliRunner()
        result = runner.invoke(cli, ["unknown-command"])
        assert result.exit_code != 0
        assert "No such command" in result.output or "Error" in result.output


class TestCompletionCommand:
    """Tests for the completion command group."""

    def test_completion_help(self):
        """Test completion group help."""
        runner = CliRunner()
        result = runner.invoke(cli, ["completion", "--help"])
        assert result.exit_code == 0
        assert "install" in result.output
        assert "status" in result.output
        assert "bash" in result.output
        assert "zsh" in result.output

    def test_completion_bash_subcommand(self):
        """Test bash completion script output."""
        runner = CliRunner()
        result = runner.invoke(cli, ["completion", "bash"])
        assert result.exit_code == 0
        assert "_SCITEX_COMPLETE=bash_source" in result.output
        assert "scitex tab completion" in result.output

    def test_completion_zsh_subcommand(self):
        """Test zsh completion script output."""
        runner = CliRunner()
        result = runner.invoke(cli, ["completion", "zsh"])
        assert result.exit_code == 0
        assert "_SCITEX_COMPLETE=zsh_source" in result.output

    def test_completion_fish_subcommand(self):
        """Test fish completion script output."""
        runner = CliRunner()
        result = runner.invoke(cli, ["completion", "fish"])
        assert result.exit_code == 0
        assert "_SCITEX_COMPLETE=fish_source" in result.output

    def test_completion_status(self):
        """Test completion status command."""
        runner = CliRunner(env={"SHELL": "/bin/bash"})
        result = runner.invoke(cli, ["completion", "status"])
        assert result.exit_code == 0
        assert "Shell Completion Status" in result.output
        assert "Shell:" in result.output
        assert "scitex in PATH:" in result.output

    def test_completion_status_shows_scitex(self):
        """Test that status shows scitex CLI status."""
        runner = CliRunner(env={"SHELL": "/bin/bash"})
        result = runner.invoke(cli, ["completion", "status"])
        assert result.exit_code == 0
        assert "scitex in PATH:" in result.output

    def test_completion_install_auto_detect_unknown(self):
        """Test error when shell cannot be auto-detected."""
        runner = CliRunner(env={"SHELL": "/bin/unknown"})
        result = runner.invoke(cli, ["completion", "install"])
        assert result.exit_code == 1
        assert "Could not auto-detect shell" in result.output

    def test_completion_install_with_shell_option(self):
        """Test install with explicit shell option."""
        runner = CliRunner()
        with tempfile.TemporaryDirectory() as tmpdir:
            bashrc = Path(tmpdir) / ".bashrc"
            bashrc.touch()

            with patch(
                "os.path.expanduser",
                side_effect=lambda x: str(bashrc) if "bashrc" in x else x,
            ):
                result = runner.invoke(
                    cli, ["completion", "install", "--shell", "bash"]
                )
                # Should succeed or show message
                assert result.exit_code in [0, 1]
                assert (
                    "completion" in result.output.lower()
                    or "install" in result.output.lower()
                )

    def test_completion_already_installed(self):
        """Test that already-installed completion is detected."""
        runner = CliRunner()
        with tempfile.TemporaryDirectory() as tmpdir:
            bashrc = Path(tmpdir) / ".bashrc"
            # Write completion marker
            bashrc.write_text("# scitex tab completion\n")

            with patch(
                "os.path.expanduser",
                side_effect=lambda x: str(bashrc) if "bashrc" in x else x,
            ):
                result = runner.invoke(
                    cli, ["completion", "install", "--shell", "bash"]
                )
                assert "already installed" in result.output.lower()

    def test_completion_default_invokes_install(self):
        """Test that completion without subcommand invokes install."""
        runner = CliRunner(env={"SHELL": "/bin/bash"})
        with tempfile.TemporaryDirectory() as tmpdir:
            bashrc = Path(tmpdir) / ".bashrc"
            bashrc.touch()

            with patch(
                "os.path.expanduser",
                side_effect=lambda x: str(bashrc) if "bashrc" in x else x,
            ):
                result = runner.invoke(cli, ["completion"])
                # Should attempt install (may succeed or fail based on env)
                assert result.exit_code in [0, 1]


class TestCLISubcommandAccess:
    """Tests for accessing subcommands."""

    def test_config_subcommand_accessible(self):
        """Test that config subcommand is accessible."""
        runner = CliRunner()
        result = runner.invoke(cli, ["config", "--help"])
        assert result.exit_code == 0
        assert "Configuration management" in result.output

    def test_cloud_subcommand_accessible(self):
        """Test that cloud subcommand is accessible."""
        runner = CliRunner()
        result = runner.invoke(cli, ["cloud", "--help"])
        assert result.exit_code == 0
        assert "Cloud operations" in result.output

    def test_convert_subcommand_accessible(self):
        """Test that convert subcommand is accessible."""
        runner = CliRunner()
        result = runner.invoke(cli, ["convert", "--help"])
        assert result.exit_code == 0
        assert "Convert and validate" in result.output

    def test_scholar_subcommand_accessible(self):
        """Test that scholar subcommand is accessible."""
        runner = CliRunner()
        result = runner.invoke(cli, ["scholar", "--help"])
        assert result.exit_code == 0
        assert "Scientific paper management" in result.output

    def test_security_subcommand_accessible(self):
        """Test that security subcommand is accessible."""
        runner = CliRunner()
        result = runner.invoke(cli, ["security", "--help"])
        assert result.exit_code == 0
        assert "Security utilities" in result.output

    def test_web_subcommand_accessible(self):
        """Test that web subcommand is accessible."""
        runner = CliRunner()
        result = runner.invoke(cli, ["web", "--help"])
        assert result.exit_code == 0
        assert "Web scraping" in result.output

    def test_writer_subcommand_accessible(self):
        """Test that writer subcommand is accessible."""
        runner = CliRunner()
        result = runner.invoke(cli, ["writer", "--help"])
        assert result.exit_code == 0
        assert "Manuscript writing" in result.output


if __name__ == "__main__":
    import os

    import pytest

    pytest.main([os.path.abspath(__file__)])

# --------------------------------------------------------------------------------
# Start of Source Code from: /home/ywatanabe/proj/scitex-code/src/scitex/cli/main.py
# --------------------------------------------------------------------------------
# #!/usr/bin/env python3
# """
# SciTeX CLI Main Entry Point
# """
#
# import os
# import sys
#
# import click
#
# from . import (
#     audio,
#     browser,
#     capture,
#     cloud,
#     config,
#     convert,
#     repro,
#     resource,
#     scholar,
#     security,
#     stats,
#     template,
#     tex,
#     web,
#     writer,
# )
#
#
# @click.group(context_settings={"help_option_names": ["-h", "--help"]})
# @click.version_option()
# def cli():
#     """
#     SciTeX - Integrated Scientific Research Platform
#
#     \b
#     Examples:
#       scitex config list                    # Show all configured paths
#       scitex config init                    # Initialize directories
#       scitex cloud login
#       scitex cloud clone ywatanabe/my-project
#       scitex scholar bibtex papers.bib --project myresearch
#       scitex scholar single --doi "10.1038/nature12373"
#       scitex security check --save
#       scitex web get-urls https://example.com
#       scitex web download-images https://example.com --output ./downloads
#       scitex audio speak "Hello world"
#       scitex capture snap --output screenshot.jpg
#       scitex resource usage
#       scitex stats recommend --data data.csv
#
#     \b
#     Enable tab-completion:
#       scitex completion          # Auto-install for your shell
#       scitex completion --show   # Show installation instructions
#     """
#     pass
#
#
# # Add command groups
# cli.add_command(audio.audio)
# cli.add_command(browser.browser)
# cli.add_command(capture.capture)
# cli.add_command(cloud.cloud)
# cli.add_command(config.config)
# cli.add_command(convert.convert)
# cli.add_command(repro.repro)
# cli.add_command(resource.resource)
# cli.add_command(scholar.scholar)
# cli.add_command(security.security)
# cli.add_command(stats.stats)
# cli.add_command(template.template)
# cli.add_command(tex.tex)
# cli.add_command(web.web)
# cli.add_command(writer.writer)
#
#
# @cli.command()
# @click.option(
#     "--shell",
#     type=click.Choice(["bash", "zsh", "fish"], case_sensitive=False),
#     help="Shell type (auto-detected if not provided)",
# )
# @click.option(
#     "--show", is_flag=True, help="Show completion script instead of installing"
# )
# def completion(shell, show):
#     """
#     Install or show shell completion for scitex commands.
#
#     \b
#     Supported shells: bash, zsh, fish
#
#     \b
#     Installation:
#       # Auto-detect shell and install
#       scitex completion
#
#       # Specify shell
#       scitex completion --shell bash
#       scitex completion --shell zsh
#
#       # Show completion script
#       scitex completion --show
#
#     \b
#     After installation, restart your shell or run:
#       source ~/.bashrc    # for bash
#       source ~/.zshrc     # for zsh
#     """
#     # Auto-detect shell if not provided
#     if not shell:
#         shell_env = os.environ.get("SHELL", "")
#         if "bash" in shell_env:
#             shell = "bash"
#         elif "zsh" in shell_env:
#             shell = "zsh"
#         elif "fish" in shell_env:
#             shell = "fish"
#         else:
#             click.secho(
#                 "Could not auto-detect shell. Please specify with --shell option.",
#                 fg="red",
#                 err=True,
#             )
#             sys.exit(1)
#
#     shell = shell.lower()
#
#     # Get full path to scitex executable
#     scitex_path = sys.argv[0]
#     if not os.path.isabs(scitex_path):
#         # If relative path, find the full path
#         import shutil
#
#         scitex_full = shutil.which("scitex") or scitex_path
#     else:
#         scitex_full = scitex_path
#
#     # Generate completion script
#     if shell == "bash":
#         rc_file = os.path.expanduser("~/.bashrc")
#         eval_line = f'eval "$(_SCITEX_COMPLETE=bash_source {scitex_full})"'
#     elif shell == "zsh":
#         rc_file = os.path.expanduser("~/.zshrc")
#         eval_line = f'eval "$(_SCITEX_COMPLETE=zsh_source {scitex_full})"'
#     elif shell == "fish":
#         rc_file = os.path.expanduser("~/.config/fish/config.fish")
#         eval_line = f"eval (env _SCITEX_COMPLETE=fish_source {scitex_full})"
#
#     if show:
#         # Just show the completion script
#         click.echo(f"Add this line to your {rc_file}:")
#         click.echo()
#         click.secho(eval_line, fg="green")
#         sys.exit(0)
#
#     # Check if already installed (and not commented out)
#     if os.path.exists(rc_file):
#         with open(rc_file) as f:
#             for line in f:
#                 # Check if the line exists and is not commented
#                 stripped = line.strip()
#                 if stripped == eval_line and not stripped.startswith("#"):
#                     click.secho(
#                         f"Tab completion is already installed in {rc_file}", fg="yellow"
#                     )
#                     click.echo()
#                     click.echo("To reload, run:")
#                     click.secho(f"  source {rc_file}", fg="cyan")
#                     sys.exit(0)
#
#     # Install completion
#     try:
#         # Create config directory if it doesn't exist (for fish)
#         os.makedirs(os.path.dirname(rc_file), exist_ok=True)
#
#         with open(rc_file, "a") as f:
#             f.write("\n# SciTeX tab completion\n")
#             f.write(f"{eval_line}\n")
#
#         click.secho(f"Successfully installed tab completion to {rc_file}", fg="green")
#         click.echo()
#         click.echo("To activate completion in current shell, run:")
#         click.secho(f"  source {rc_file}", fg="cyan")
#         click.echo()
#         click.echo("Or restart your shell.")
#         sys.exit(0)
#
#     except Exception as e:
#         click.secho(f"ERROR: Failed to install completion: {e}", fg="red", err=True)
#         click.echo()
#         click.echo("You can manually add this line to your shell config:")
#         click.secho(eval_line, fg="green")
#         sys.exit(1)
#
#
# if __name__ == "__main__":
#     cli()

# --------------------------------------------------------------------------------
# End of Source Code from: /home/ywatanabe/proj/scitex-code/src/scitex/cli/main.py
# --------------------------------------------------------------------------------
