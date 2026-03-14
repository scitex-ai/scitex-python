#!/usr/bin/env python3
"""Tests for scitex.cli.config - Configuration CLI commands."""

import json
import os
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from click.testing import CliRunner

from scitex.cli.config import config


class TestConfigGroup:
    """Tests for the config command group."""

    def test_config_help(self):
        """Test that config help is displayed correctly."""
        runner = CliRunner()
        result = runner.invoke(config, ["--help"])
        assert result.exit_code == 0
        assert "Configuration management" in result.output

    def test_config_has_subcommands(self):
        """Test that all expected subcommands are registered."""
        runner = CliRunner()
        result = runner.invoke(config, ["--help"])
        expected_commands = ["list", "init", "show"]
        for cmd in expected_commands:
            assert cmd in result.output, f"Command '{cmd}' not found in config help"


class TestConfigList:
    """Tests for the config list command."""

    def test_list_default(self):
        """Test config list with default options."""
        runner = CliRunner()
        with tempfile.TemporaryDirectory() as tmpdir:
            base_path = Path(tmpdir)
            # Mock at the source module level where it's imported from
            with patch("scitex.config.ScitexPaths") as mock_paths_cls:
                mock_paths = MagicMock()
                mock_paths.base = base_path  # Use real path that exists
                mock_paths.list_all.return_value = {
                    "logs": base_path / "logs",
                    "cache": base_path / "cache",
                }
                mock_paths_cls.return_value = mock_paths

                result = runner.invoke(config, ["list"])
                assert result.exit_code == 0
                assert "SciTeX Configuration" in result.output
                assert "Base Directory" in result.output

    def test_list_with_env_flag(self):
        """Test config list with --env flag."""
        runner = CliRunner()
        with tempfile.TemporaryDirectory() as tmpdir:
            base_path = Path(tmpdir)
            with patch("scitex.config.ScitexPaths") as mock_paths_cls:
                mock_paths = MagicMock()
                mock_paths.base = base_path  # Use real path that exists
                mock_paths.list_all.return_value = {}
                mock_paths_cls.return_value = mock_paths

                result = runner.invoke(config, ["list", "--env"])
                assert result.exit_code == 0
                assert "Environment Variables" in result.output
                assert "SCITEX_DIR" in result.output

    def test_list_with_json_flag(self):
        """Test config list with --json flag."""
        runner = CliRunner()
        with patch("scitex.config.ScitexPaths") as mock_paths_cls:
            mock_paths = MagicMock()
            mock_paths.base = Path("/tmp/test-scitex")
            mock_paths.list_all.return_value = {
                "logs": Path("/tmp/test-scitex/logs"),
            }
            mock_paths_cls.return_value = mock_paths

            result = runner.invoke(config, ["list", "--json"])
            assert result.exit_code == 0
            # Verify output is valid JSON
            output_json = json.loads(result.output)
            data = output_json.get("data", output_json)
            assert "paths" in data
            assert "logs" in data["paths"]

    def test_list_with_json_and_env(self):
        """Test config list with both --json and --env flags."""
        runner = CliRunner()
        with patch("scitex.config.ScitexPaths") as mock_paths_cls:
            mock_paths = MagicMock()
            mock_paths.base = Path("/tmp/test-scitex")
            mock_paths.list_all.return_value = {}
            mock_paths_cls.return_value = mock_paths

            result = runner.invoke(config, ["list", "--json", "--env"])
            assert result.exit_code == 0
            output_json = json.loads(result.output)
            data = output_json.get("data", output_json)
            assert "environment" in data
            assert "SCITEX_DIR" in data["environment"]

    def test_list_with_exists_flag(self):
        """Test config list with --exists flag filters non-existing paths."""
        runner = CliRunner()
        with tempfile.TemporaryDirectory() as tmpdir:
            base_path = Path(tmpdir)
            # Create one directory that exists
            existing_path = base_path / "logs"
            existing_path.mkdir()
            # Reference one that doesn't exist
            non_existing_path = base_path / "cache"

            with patch("scitex.config.ScitexPaths") as mock_paths_cls:
                mock_paths = MagicMock()
                mock_paths.base = base_path

                mock_paths.list_all.return_value = {
                    "logs": existing_path,
                    "cache": non_existing_path,
                }
                mock_paths_cls.return_value = mock_paths

                result = runner.invoke(config, ["list", "--exists"])
                assert result.exit_code == 0


class TestConfigInit:
    """Tests for the config init command."""

    def test_init_default(self):
        """Test config init creates directories."""
        runner = CliRunner()
        with tempfile.TemporaryDirectory() as tmpdir:
            with patch("scitex.config.ScitexPaths") as mock_paths_cls:
                mock_paths = MagicMock()

                # Create actual paths in temp dir for testing
                logs_path = Path(tmpdir) / "logs"
                cache_path = Path(tmpdir) / "cache"

                mock_paths.list_all.return_value = {
                    "logs": logs_path,
                    "cache": cache_path,
                }
                mock_paths_cls.return_value = mock_paths

                result = runner.invoke(config, ["init"])
                assert result.exit_code == 0
                assert "Initializing SciTeX directories" in result.output
                # Directories should be created
                assert logs_path.exists()
                assert cache_path.exists()

    def test_init_dry_run(self):
        """Test config init with --dry-run flag."""
        runner = CliRunner()
        with tempfile.TemporaryDirectory() as tmpdir:
            with patch("scitex.config.ScitexPaths") as mock_paths_cls:
                mock_paths = MagicMock()

                # Create paths that don't exist yet
                logs_path = Path(tmpdir) / "new_logs"
                cache_path = Path(tmpdir) / "new_cache"

                mock_paths.list_all.return_value = {
                    "logs": logs_path,
                    "cache": cache_path,
                }
                mock_paths_cls.return_value = mock_paths

                result = runner.invoke(config, ["init", "--dry-run"])
                assert result.exit_code == 0
                assert "WOULD CREATE" in result.output
                # Directories should NOT be created in dry-run mode
                assert not logs_path.exists()
                assert not cache_path.exists()

    def test_init_existing_directories(self):
        """Test config init reports existing directories."""
        runner = CliRunner()
        with tempfile.TemporaryDirectory() as tmpdir:
            with patch("scitex.config.ScitexPaths") as mock_paths_cls:
                mock_paths = MagicMock()

                # Create a path that already exists
                existing_path = Path(tmpdir) / "existing"
                existing_path.mkdir()

                mock_paths.list_all.return_value = {
                    "existing": existing_path,
                }
                mock_paths_cls.return_value = mock_paths

                result = runner.invoke(config, ["init"])
                assert result.exit_code == 0
                assert "EXISTS" in result.output


class TestConfigShow:
    """Tests for the config show command."""

    def test_show_valid_path(self):
        """Test config show with a valid path name."""
        runner = CliRunner()
        with patch("scitex.config.ScitexPaths") as mock_paths_cls:
            mock_paths = MagicMock()
            mock_paths.logs = Path("/tmp/test-scitex/logs")
            mock_paths.list_all.return_value = {"logs": mock_paths.logs}
            mock_paths_cls.return_value = mock_paths

            result = runner.invoke(config, ["show", "logs"])
            assert result.exit_code == 0
            assert "/tmp/test-scitex/logs" in result.output

    def test_show_invalid_path(self):
        """Test config show with an invalid path name."""
        runner = CliRunner()
        with patch("scitex.config.ScitexPaths") as mock_paths_cls:
            mock_paths = MagicMock()
            # Configure hasattr to return False for invalid_path
            mock_paths.configure_mock(**{"invalid_path": None})
            # Make hasattr return False by removing the attribute
            del mock_paths.invalid_path
            mock_paths.list_all.return_value = {"logs": Path("/tmp/logs")}
            mock_paths_cls.return_value = mock_paths

            result = runner.invoke(config, ["show", "invalid_path"])
            assert result.exit_code == 1
            assert "Unknown path" in result.output

    def test_show_displays_available_paths(self):
        """Test that show error message includes available paths."""
        runner = CliRunner()
        with patch("scitex.config.ScitexPaths") as mock_paths_cls:
            mock_paths = MagicMock()
            mock_paths.list_all.return_value = {
                "logs": Path("/tmp/logs"),
                "cache": Path("/tmp/cache"),
            }
            # Make hasattr return False for unknown
            del mock_paths.unknown
            mock_paths_cls.return_value = mock_paths

            result = runner.invoke(config, ["show", "unknown"])
            assert result.exit_code == 1
            assert "Available paths" in result.output


class TestConfigIntegration:
    """Integration tests for config commands."""

    def test_list_then_show(self):
        """Test listing paths and then showing a specific path."""
        runner = CliRunner()
        with tempfile.TemporaryDirectory() as tmpdir:
            base_path = Path(tmpdir)
            logs_path = base_path / "logs"

            with patch("scitex.config.ScitexPaths") as mock_paths_cls:
                mock_paths = MagicMock()
                mock_paths.base = base_path
                mock_paths.logs = logs_path
                mock_paths.list_all.return_value = {
                    "logs": logs_path,
                }
                mock_paths_cls.return_value = mock_paths

                # First, list all
                result1 = runner.invoke(config, ["list"])
                assert result1.exit_code == 0

                # Then show a specific path
                result2 = runner.invoke(config, ["show", "logs"])
                assert result2.exit_code == 0
                assert str(logs_path) in result2.output


if __name__ == "__main__":
    import os

    import pytest

    pytest.main([os.path.abspath(__file__)])

# --------------------------------------------------------------------------------
# Start of Source Code from: /home/ywatanabe/proj/scitex-code/src/scitex/cli/config.py
# --------------------------------------------------------------------------------
# #!/usr/bin/env python3
# # -*- coding: utf-8 -*-
# # Timestamp: "2025-12-09 (ywatanabe)"
# # File: /home/ywatanabe/proj/scitex-code/src/scitex/cli/config.py
#
# """
# SciTeX Configuration CLI Commands
#
# Commands for managing SciTeX configuration and paths.
# """
#
# import os
# import click
#
#
# @click.group()
# def config():
#     """
#     Configuration management commands.
#
#     \b
#     Examples:
#       scitex config list          # Show all configured paths
#       scitex config list --env    # Show environment variables
#       scitex config init          # Initialize all directories
#     """
#     pass
#
#
# @config.command("list")
# @click.option(
#     "--env",
#     is_flag=True,
#     help="Show relevant environment variables",
# )
# @click.option(
#     "--exists",
#     is_flag=True,
#     help="Only show paths that exist",
# )
# @click.option(
#     "--json",
#     "as_json",
#     is_flag=True,
#     help="Output as JSON",
# )
# def list_config(env, exists, as_json):
#     """
#     List all configured paths and settings.
#
#     \b
#     Examples:
#       scitex config list            # Show all paths
#       scitex config list --env      # Include environment variables
#       scitex config list --exists   # Only show existing directories
#       scitex config list --json     # Output as JSON
#     """
#     from scitex.config import ScitexPaths, get_scitex_dir
#
#     paths = ScitexPaths()
#     all_paths = paths.list_all()
#
#     if as_json:
#         import json
#
#         output = {}
#         if env:
#             output["environment"] = {
#                 "SCITEX_DIR": os.getenv("SCITEX_DIR", "(not set)"),
#             }
#         output["paths"] = {k: str(v) for k, v in all_paths.items()}
#         if exists:
#             output["paths"] = {
#                 k: v for k, v in output["paths"].items() if all_paths[k].exists()
#             }
#         click.echo(json.dumps(output, indent=2))
#         return
#
#     # Header
#     click.secho("SciTeX Configuration", fg="cyan", bold=True)
#     click.echo("=" * 50)
#     click.echo()
#
#     # Environment variables
#     if env:
#         click.secho("Environment Variables:", fg="yellow", bold=True)
#         scitex_dir = os.getenv("SCITEX_DIR")
#         if scitex_dir:
#             click.echo(f"  SCITEX_DIR = {scitex_dir}")
#         else:
#             click.echo(f"  SCITEX_DIR = (not set, using default: ~/.scitex)")
#         click.echo()
#
#     # Base directory
#     click.secho("Base Directory:", fg="yellow", bold=True)
#     base = paths.base
#     exists_mark = (
#         click.style("✓", fg="green") if base.exists() else click.style("✗", fg="red")
#     )
#     click.echo(f"  {exists_mark} {base}")
#     click.echo()
#
#     # All paths
#     click.secho("Configured Paths:", fg="yellow", bold=True)
#
#     # Group paths by category
#     categories = {
#         "Core": ["logs", "cache", "function_cache", "capture", "screenshots", "rng"],
#         "Browser": [
#             "browser",
#             "browser_screenshots",
#             "browser_sessions",
#             "browser_persistent",
#             "test_monitor",
#         ],
#         "Cache": ["impact_factor_cache", "openathens_cache"],
#         "Scholar": ["scholar", "scholar_cache", "scholar_library"],
#         "Other": ["writer"],
#     }
#
#     for category, path_names in categories.items():
#         click.secho(f"\n  {category}:", fg="blue")
#         for name in path_names:
#             if name not in all_paths:
#                 continue
#             path = all_paths[name]
#             if exists and not path.exists():
#                 continue
#             exists_mark = (
#                 click.style("✓", fg="green")
#                 if path.exists()
#                 else click.style("✗", fg="red")
#             )
#             # Show relative to base if under base
#             try:
#                 rel_path = path.relative_to(paths.base)
#                 display_path = f"$SCITEX_DIR/{rel_path}"
#             except ValueError:
#                 display_path = str(path)
#             click.echo(f"    {exists_mark} {name:<22} {display_path}")
#
#     click.echo()
#
#
# @config.command("init")
# @click.option(
#     "--dry-run",
#     is_flag=True,
#     help="Show what would be created without creating",
# )
# def init_config(dry_run):
#     """
#     Initialize all SciTeX directories.
#
#     Creates all standard directories if they don't exist.
#
#     \b
#     Examples:
#       scitex config init            # Create all directories
#       scitex config init --dry-run  # Show what would be created
#     """
#     from scitex.config import ScitexPaths
#
#     paths = ScitexPaths()
#     all_paths = paths.list_all()
#
#     click.secho("Initializing SciTeX directories...", fg="cyan", bold=True)
#     click.echo()
#
#     created = 0
#     existed = 0
#
#     for name, path in all_paths.items():
#         if path.exists():
#             existed += 1
#             click.echo(f"  {click.style('EXISTS', fg='yellow')}: {path}")
#         else:
#             if dry_run:
#                 click.echo(f"  {click.style('WOULD CREATE', fg='blue')}: {path}")
#             else:
#                 path.mkdir(parents=True, exist_ok=True)
#                 click.echo(f"  {click.style('CREATED', fg='green')}: {path}")
#             created += 1
#
#     click.echo()
#     if dry_run:
#         click.echo(f"Would create {created} directories ({existed} already exist)")
#     else:
#         click.echo(f"Created {created} directories ({existed} already existed)")
#
#
# @config.command("show")
# @click.argument("path_name")
# def show_path(path_name):
#     """
#     Show a specific configured path.
#
#     \b
#     PATH_NAME can be one of:
#       base, logs, cache, function_cache, capture, screenshots,
#       browser, browser_screenshots, browser_sessions, browser_persistent,
#       test_monitor, impact_factor_cache, openathens_cache,
#       scholar, scholar_cache, scholar_library, writer, rng
#
#     \b
#     Examples:
#       scitex config show logs
#       scitex config show scholar_library
#     """
#     from scitex.config import ScitexPaths
#
#     paths = ScitexPaths()
#
#     if hasattr(paths, path_name):
#         path = getattr(paths, path_name)
#         click.echo(str(path))
#     else:
#         available = list(paths.list_all().keys())
#         click.secho(f"Unknown path: {path_name}", fg="red", err=True)
#         click.echo(f"Available paths: {', '.join(available)}", err=True)
#         raise SystemExit(1)
#
#
# # EOF

# --------------------------------------------------------------------------------
# End of Source Code from: /home/ywatanabe/proj/scitex-code/src/scitex/cli/config.py
# --------------------------------------------------------------------------------
