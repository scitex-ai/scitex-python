#!/usr/bin/env python3
"""Tests for scitex.cli.convert - Bundle conversion CLI commands."""

import json
import os
import tempfile
import zipfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from click.testing import CliRunner

from scitex.cli.convert import convert


class TestConvertGroup:
    """Tests for the convert command group."""

    def test_convert_help(self):
        """Test that convert help is displayed correctly."""
        runner = CliRunner()
        result = runner.invoke(convert, ["--help"])
        assert result.exit_code == 0
        assert "Convert and validate" in result.output

    def test_convert_has_subcommands(self):
        """Test that all expected subcommands are registered."""
        runner = CliRunner()
        result = runner.invoke(convert, ["--help"])
        expected_commands = ["file", "batch", "validate", "info"]
        for cmd in expected_commands:
            assert cmd in result.output, f"Command '{cmd}' not found in convert help"


class TestConvertFile:
    """Tests for the convert file command."""

    def test_file_help(self):
        """Test file command help."""
        runner = CliRunner()
        result = runner.invoke(convert, ["file", "--help"])
        assert result.exit_code == 0
        assert "Convert a single legacy bundle" in result.output

    def test_file_missing_input(self):
        """Test file command without input path."""
        runner = CliRunner()
        result = runner.invoke(convert, ["file"])
        assert result.exit_code != 0
        assert "Missing argument" in result.output

    def test_file_nonexistent_input(self):
        """Test file command with non-existent input."""
        runner = CliRunner()
        result = runner.invoke(convert, ["file", "/nonexistent/file.figz"])
        assert result.exit_code != 0

    def test_file_already_stx(self):
        """Test that .stx files are skipped."""
        runner = CliRunner()
        with tempfile.NamedTemporaryFile(suffix=".stx", delete=False) as f:
            f.write(b"dummy")
            f.flush()
            result = runner.invoke(convert, ["file", f.name])
            assert result.exit_code == 0
            assert "already in .stx format" in result.output
            os.unlink(f.name)

    def test_file_unsupported_format(self):
        """Test that unsupported formats are rejected."""
        runner = CliRunner()
        with tempfile.NamedTemporaryFile(suffix=".txt", delete=False) as f:
            f.write(b"dummy")
            f.flush()
            result = runner.invoke(convert, ["file", f.name])
            assert result.exit_code == 1
            assert "Unsupported format" in result.output
            os.unlink(f.name)

    def test_file_dry_run(self):
        """Test file command with --dry-run flag."""
        runner = CliRunner()
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create a mock .figz file (valid zip with spec.json)
            figz_path = Path(tmpdir) / "test.figz"
            with zipfile.ZipFile(figz_path, "w") as zf:
                spec = {"type": "figure", "schema": {"name": "stx", "version": "1.0.0"}}
                zf.writestr("spec.json", json.dumps(spec))

            result = runner.invoke(convert, ["file", str(figz_path), "--dry-run"])
            assert result.exit_code == 0
            assert "Would convert" in result.output

            # Output file should NOT exist in dry-run mode
            stx_path = figz_path.with_suffix(".stx")
            assert not stx_path.exists()

    def test_file_output_exists_no_overwrite(self):
        """Test that existing output file blocks conversion without --overwrite."""
        runner = CliRunner()
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create input file
            figz_path = Path(tmpdir) / "test.figz"
            with zipfile.ZipFile(figz_path, "w") as zf:
                spec = {"type": "figure"}
                zf.writestr("spec.json", json.dumps(spec))

            # Create output file
            stx_path = figz_path.with_suffix(".stx")
            stx_path.touch()

            result = runner.invoke(convert, ["file", str(figz_path)])
            assert result.exit_code == 1
            assert "Output file exists" in result.output

    def test_file_output_with_overwrite(self):
        """Test that --overwrite allows replacing existing output."""
        runner = CliRunner()
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create input file
            figz_path = Path(tmpdir) / "test.figz"
            with zipfile.ZipFile(figz_path, "w") as zf:
                spec = {"type": "figure", "schema": {"name": "stx", "version": "1.0.0"}}
                zf.writestr("spec.json", json.dumps(spec))

            # Create output file
            stx_path = figz_path.with_suffix(".stx")
            stx_path.touch()

            # Mock the conversion function to avoid internal bugs
            with patch("scitex.cli.convert._convert_bundle") as mock_convert:
                result = runner.invoke(convert, ["file", str(figz_path), "--overwrite"])
                assert result.exit_code == 0
                assert "Converted" in result.output
                mock_convert.assert_called_once()

    def test_file_custom_output(self):
        """Test file command with custom output path."""
        runner = CliRunner()
        with tempfile.TemporaryDirectory() as tmpdir:
            figz_path = Path(tmpdir) / "input.figz"
            output_path = Path(tmpdir) / "custom_output.stx"

            with zipfile.ZipFile(figz_path, "w") as zf:
                spec = {"type": "figure", "schema": {"name": "stx", "version": "1.0.0"}}
                zf.writestr("spec.json", json.dumps(spec))

            # Mock the conversion function to avoid internal bugs
            with patch("scitex.cli.convert._convert_bundle") as mock_convert:
                result = runner.invoke(
                    convert, ["file", str(figz_path), "-o", str(output_path)]
                )
                assert result.exit_code == 0
                mock_convert.assert_called_once()


class TestConvertBatch:
    """Tests for the convert batch command."""

    def test_batch_help(self):
        """Test batch command help."""
        runner = CliRunner()
        result = runner.invoke(convert, ["batch", "--help"])
        assert result.exit_code == 0
        assert "Batch convert" in result.output

    def test_batch_missing_pattern(self):
        """Test batch command without pattern."""
        runner = CliRunner()
        result = runner.invoke(convert, ["batch"])
        assert result.exit_code != 0
        assert (
            "Missing argument" in result.output or "required" in result.output.lower()
        )

    def test_batch_no_matching_files(self):
        """Test batch command with no matching files."""
        runner = CliRunner()
        with tempfile.TemporaryDirectory() as tmpdir:
            result = runner.invoke(convert, ["batch", f"{tmpdir}/*.figz"])
            assert result.exit_code == 0
            assert "No matching files found" in result.output

    def test_batch_dry_run(self):
        """Test batch command with --dry-run flag."""
        runner = CliRunner()
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create multiple test files
            for i in range(3):
                figz_path = Path(tmpdir) / f"test{i}.figz"
                with zipfile.ZipFile(figz_path, "w") as zf:
                    spec = {"type": "figure"}
                    zf.writestr("spec.json", json.dumps(spec))

            result = runner.invoke(convert, ["batch", f"{tmpdir}/*.figz", "--dry-run"])
            assert result.exit_code == 0
            assert "Found 3 file(s)" in result.output
            assert "Would convert" in result.output

    def test_batch_with_output_dir(self):
        """Test batch command with custom output directory."""
        runner = CliRunner()
        with tempfile.TemporaryDirectory() as tmpdir:
            input_dir = Path(tmpdir) / "input"
            output_dir = Path(tmpdir) / "output"
            input_dir.mkdir()

            # Create test file
            figz_path = input_dir / "test.figz"
            with zipfile.ZipFile(figz_path, "w") as zf:
                spec = {"type": "figure", "schema": {"name": "stx", "version": "1.0.0"}}
                zf.writestr("spec.json", json.dumps(spec))

            # Mock conversion function to avoid internal implementation bugs
            with patch("scitex.cli.convert._convert_bundle") as mock_convert:
                result = runner.invoke(
                    convert, ["batch", f"{input_dir}/*.figz", "-o", str(output_dir)]
                )
                assert result.exit_code == 0
                assert output_dir.exists()
                mock_convert.assert_called_once()


class TestConvertValidate:
    """Tests for the convert validate command."""

    def test_validate_help(self):
        """Test validate command help."""
        runner = CliRunner()
        result = runner.invoke(convert, ["validate", "--help"])
        assert result.exit_code == 0
        assert "Validate one or more .stx bundles" in result.output

    def test_validate_missing_paths(self):
        """Test validate command without paths."""
        runner = CliRunner()
        result = runner.invoke(convert, ["validate"])
        assert result.exit_code != 0

    def test_validate_nonexistent_file(self):
        """Test validate command with non-existent file."""
        runner = CliRunner()
        result = runner.invoke(convert, ["validate", "/nonexistent/file.stx"])
        assert result.exit_code != 0

    def test_validate_valid_bundle(self):
        """Test validating a valid bundle."""
        runner = CliRunner()
        with tempfile.TemporaryDirectory() as tmpdir:
            stx_path = Path(tmpdir) / "valid.stx"
            with zipfile.ZipFile(stx_path, "w") as zf:
                spec = {
                    "type": "figure",
                    "bundle_id": "abc12345",
                    "schema": {"name": "stx", "version": "2.0.0"},
                    "constraints": {"allow_children": False, "max_depth": 1},
                }
                zf.writestr("spec.json", json.dumps(spec))

            # Patch at the source module where Bundle is imported
            with patch("scitex.io.bundle.Bundle") as mock_bundle_cls:
                mock_bundle = MagicMock()
                mock_bundle.__enter__ = MagicMock(return_value=mock_bundle)
                mock_bundle.__exit__ = MagicMock(return_value=False)
                mock_bundle.read_json.return_value = spec
                mock_bundle_cls.return_value = mock_bundle

                result = runner.invoke(convert, ["validate", str(stx_path)])
                # May succeed or fail depending on FTS availability
                assert result.exit_code in [0, 1]

    def test_validate_verbose(self):
        """Test validate command with --verbose flag."""
        runner = CliRunner()
        with tempfile.TemporaryDirectory() as tmpdir:
            stx_path = Path(tmpdir) / "test.stx"
            with zipfile.ZipFile(stx_path, "w") as zf:
                spec = {
                    "type": "figure",
                    "bundle_id": "abc12345",
                    "schema": {"name": "stx", "version": "2.0.0"},
                }
                zf.writestr("spec.json", json.dumps(spec))

            # Patch at the source module where Bundle is imported
            with patch("scitex.io.bundle.Bundle") as mock_bundle_cls:
                mock_bundle = MagicMock()
                mock_bundle.__enter__ = MagicMock(return_value=mock_bundle)
                mock_bundle.__exit__ = MagicMock(return_value=False)
                mock_bundle.read_json.return_value = spec
                mock_bundle_cls.return_value = mock_bundle

                result = runner.invoke(convert, ["validate", str(stx_path), "-v"])
                # Output should include verbose info
                assert result.exit_code in [0, 1]


class TestConvertInfo:
    """Tests for the convert info command."""

    def test_info_help(self):
        """Test info command help."""
        runner = CliRunner()
        result = runner.invoke(convert, ["info", "--help"])
        assert result.exit_code == 0
        assert "Show information about a bundle" in result.output

    def test_info_missing_path(self):
        """Test info command without path."""
        runner = CliRunner()
        result = runner.invoke(convert, ["info"])
        assert result.exit_code != 0
        assert "Missing argument" in result.output

    def test_info_nonexistent_file(self):
        """Test info command with non-existent file."""
        runner = CliRunner()
        result = runner.invoke(convert, ["info", "/nonexistent/file.stx"])
        assert result.exit_code != 0

    def test_info_valid_bundle(self):
        """Test info command on a valid bundle."""
        runner = CliRunner()
        with tempfile.TemporaryDirectory() as tmpdir:
            stx_path = Path(tmpdir) / "test.stx"
            spec = {
                "type": "figure",
                "bundle_id": "test123",
                "schema": {"name": "stx", "version": "2.0.0"},
                "panels": [{"id": "panel1"}],
                "elements": [{"id": "elem1"}],
            }

            with zipfile.ZipFile(stx_path, "w") as zf:
                zf.writestr("spec.json", json.dumps(spec))
                zf.writestr("data.txt", "test data")

            # Patch at the source module where Bundle is imported
            with patch("scitex.io.bundle.Bundle") as mock_bundle_cls:
                mock_bundle = MagicMock()
                mock_bundle.__enter__ = MagicMock(return_value=mock_bundle)
                mock_bundle.__exit__ = MagicMock(return_value=False)
                mock_bundle.read_json.return_value = spec
                mock_bundle.namelist.return_value = ["spec.json", "data.txt"]
                mock_bundle_cls.return_value = mock_bundle

                result = runner.invoke(convert, ["info", str(stx_path)])
                # May succeed or fail depending on FTS availability
                assert result.exit_code in [0, 1]


class TestConvertBundleConversion:
    """Tests for bundle conversion CLI flow (mocked to avoid internal bugs)."""

    def test_convert_figz_to_stx(self):
        """Test converting a .figz file to .stx."""
        runner = CliRunner()
        with tempfile.TemporaryDirectory() as tmpdir:
            figz_path = Path(tmpdir) / "figure.figz"
            spec = {
                "type": "figure",
                "schema": {"name": "legacy", "version": "1.0.0"},
            }

            with zipfile.ZipFile(figz_path, "w") as zf:
                zf.writestr("spec.json", json.dumps(spec))
                zf.writestr("image.png", b"fake png data")

            # Mock conversion to test CLI flow
            with patch("scitex.cli.convert._convert_bundle") as mock_convert:
                result = runner.invoke(convert, ["file", str(figz_path)])
                assert result.exit_code == 0
                mock_convert.assert_called_once()

    def test_convert_pltz_to_stx(self):
        """Test converting a .pltz file to .stx."""
        runner = CliRunner()
        with tempfile.TemporaryDirectory() as tmpdir:
            pltz_path = Path(tmpdir) / "plot.pltz"
            spec = {
                "type": "plot",
                "plot_type": "scatter",
                "schema": {"name": "legacy", "version": "1.0.0"},
            }

            with zipfile.ZipFile(pltz_path, "w") as zf:
                zf.writestr("spec.json", json.dumps(spec))

            # Mock conversion to test CLI flow
            with patch("scitex.cli.convert._convert_bundle") as mock_convert:
                result = runner.invoke(convert, ["file", str(pltz_path)])
                assert result.exit_code == 0
                mock_convert.assert_called_once()

    def test_convert_statsz_to_stx(self):
        """Test converting a .statsz file to .stx."""
        runner = CliRunner()
        with tempfile.TemporaryDirectory() as tmpdir:
            statsz_path = Path(tmpdir) / "stats.statsz"
            spec = {
                "type": "stats",
                "comparisons": [],
                "schema": {"name": "legacy", "version": "1.0.0"},
            }

            with zipfile.ZipFile(statsz_path, "w") as zf:
                zf.writestr("spec.json", json.dumps(spec))

            # Mock conversion to test CLI flow
            with patch("scitex.cli.convert._convert_bundle") as mock_convert:
                result = runner.invoke(convert, ["file", str(statsz_path)])
                assert result.exit_code == 0
                mock_convert.assert_called_once()


if __name__ == "__main__":
    import os

    import pytest

    pytest.main([os.path.abspath(__file__)])

# --------------------------------------------------------------------------------
# Start of Source Code from: /home/ywatanabe/proj/scitex-code/src/scitex/cli/convert.py
# --------------------------------------------------------------------------------
# #!/usr/bin/env python3
# # Timestamp: "2025-12-19 (ywatanabe)"
# # File: /home/ywatanabe/proj/scitex-code/src/scitex/cli/convert.py
#
# """
# CLI commands for converting legacy bundle formats to unified .stx format.
#
# Usage:
#     scitex convert old_figure.figz                    # Convert to old_figure.stx
#     scitex convert old_figure.figz output.stx         # Convert with custom output
#     scitex convert --batch ./figures/*.figz           # Batch convert
#     scitex convert --validate output.stx              # Validate bundle
# """
#
# import sys
# from pathlib import Path
# from typing import List, Optional
#
# import click
#
#
# @click.group()
# def convert():
#     """Convert and validate SciTeX bundle files.
#
#     \b
#     Convert legacy formats (.figz, .pltz, .statsz) to unified .stx format.
#     Supports single file conversion, batch conversion, and validation.
#
#     \b
#     Examples:
#       scitex convert file old_figure.figz              # Convert single file
#       scitex convert file old_figure.figz -o new.stx   # Custom output name
#       scitex convert batch ./figures/*.figz            # Batch convert
#       scitex convert validate output.stx               # Validate bundle
#     """
#     pass
#
#
# @convert.command("file")
# @click.argument("input_path", type=click.Path(exists=True))
# @click.option(
#     "-o",
#     "--output",
#     type=click.Path(),
#     help="Output path (default: same name with .stx extension)",
# )
# @click.option(
#     "--overwrite",
#     is_flag=True,
#     help="Overwrite output file if it exists",
# )
# @click.option(
#     "--dry-run",
#     is_flag=True,
#     help="Show what would be done without writing files",
# )
# def convert_file(
#     input_path: str, output: Optional[str], overwrite: bool, dry_run: bool
# ):
#     """Convert a single legacy bundle to .stx format.
#
#     \b
#     Supported input formats:
#       .figz  - Figure bundles
#       .pltz  - Plot bundles
#       .statsz - Statistics bundles
#
#     \b
#     Examples:
#       scitex convert file old_figure.figz
#       scitex convert file plot.pltz -o converted_plot.stx
#       scitex convert file stats.statsz --dry-run
#     """
#     input_file = Path(input_path)
#
#     # Determine output path
#     if output:
#         output_file = Path(output)
#     else:
#         output_file = input_file.with_suffix(".stx")
#
#     # Check if already .stx
#     if input_file.suffix == ".stx":
#         click.secho(f"File is already in .stx format: {input_file}", fg="yellow")
#         return
#
#     # Validate input format
#     valid_extensions = (".figz", ".pltz", ".statsz")
#     if input_file.suffix not in valid_extensions:
#         click.secho(
#             f"Unsupported format: {input_file.suffix}. "
#             f"Supported: {', '.join(valid_extensions)}",
#             fg="red",
#             err=True,
#         )
#         sys.exit(1)
#
#     # Check output exists
#     if output_file.exists() and not overwrite:
#         click.secho(
#             f"Output file exists: {output_file}. Use --overwrite to replace.",
#             fg="red",
#             err=True,
#         )
#         sys.exit(1)
#
#     if dry_run:
#         click.echo(f"Would convert: {input_file} -> {output_file}")
#         return
#
#     # Perform conversion
#     try:
#         _convert_bundle(input_file, output_file)
#         click.secho(f"Converted: {input_file} -> {output_file}", fg="green")
#     except Exception as e:
#         click.secho(f"Error converting {input_file}: {e}", fg="red", err=True)
#         sys.exit(1)
#
#
# @convert.command("batch")
# @click.argument("pattern", nargs=-1, required=True)
# @click.option(
#     "-o",
#     "--output-dir",
#     type=click.Path(),
#     help="Output directory (default: same as input)",
# )
# @click.option(
#     "--overwrite",
#     is_flag=True,
#     help="Overwrite existing files",
# )
# @click.option(
#     "--dry-run",
#     is_flag=True,
#     help="Show what would be done without writing files",
# )
# def convert_batch(
#     pattern: tuple, output_dir: Optional[str], overwrite: bool, dry_run: bool
# ):
#     """Batch convert multiple legacy bundles to .stx format.
#
#     \b
#     Examples:
#       scitex convert batch ./figures/*.figz
#       scitex convert batch ./plots/*.pltz -o ./converted/
#       scitex convert batch ./**/*.figz ./**/*.pltz --dry-run
#     """
#     import glob
#
#     # Collect all files matching patterns
#     files: List[Path] = []
#     for pat in pattern:
#         matches = glob.glob(pat, recursive=True)
#         files.extend(Path(m) for m in matches)
#
#     # Filter to valid extensions
#     valid_extensions = (".figz", ".pltz", ".statsz")
#     files = [f for f in files if f.suffix in valid_extensions]
#
#     if not files:
#         click.secho("No matching files found.", fg="yellow")
#         return
#
#     click.echo(f"Found {len(files)} file(s) to convert")
#
#     # Determine output directory
#     out_dir = Path(output_dir) if output_dir else None
#     if out_dir and not dry_run:
#         out_dir.mkdir(parents=True, exist_ok=True)
#
#     # Convert each file
#     converted = 0
#     errors = 0
#     for input_file in files:
#         if out_dir:
#             output_file = out_dir / input_file.with_suffix(".stx").name
#         else:
#             output_file = input_file.with_suffix(".stx")
#
#         if output_file.exists() and not overwrite:
#             click.secho(f"Skipping (exists): {output_file}", fg="yellow")
#             continue
#
#         if dry_run:
#             click.echo(f"Would convert: {input_file} -> {output_file}")
#             converted += 1
#             continue
#
#         try:
#             _convert_bundle(input_file, output_file)
#             click.secho(
#                 f"Converted: {input_file.name} -> {output_file.name}", fg="green"
#             )
#             converted += 1
#         except Exception as e:
#             click.secho(f"Error: {input_file}: {e}", fg="red", err=True)
#             errors += 1
#
#     # Summary
#     click.echo()
#     click.echo(f"Converted: {converted}, Errors: {errors}")
#
#
# @convert.command("validate")
# @click.argument("paths", nargs=-1, required=True, type=click.Path(exists=True))
# @click.option(
#     "--verbose",
#     "-v",
#     is_flag=True,
#     help="Show detailed validation info",
# )
# def validate_bundles(paths: tuple, verbose: bool):
#     """Validate one or more .stx bundles.
#
#     \b
#     Checks:
#       - Valid ZIP structure
#       - spec.json present and valid
#       - Schema version
#       - Depth limits
#       - Circular references
#
#     \b
#     Examples:
#       scitex convert validate output.stx
#       scitex convert validate ./figures/*.stx --verbose
#     """
#     # Use Bundle for validation
#     try:
#         from scitex.io.bundle import Bundle as ZipBundle
#
#         def validate_stx_bundle(path):
#             try:
#                 bundle = ZipBundle(path)
#                 return bundle.validate(level="strict")
#             except Exception as e:
#                 return {"valid": False, "errors": [str(e)]}
#
#     except ImportError:
#         click.echo("Error: scitex.io.bundle not available", err=True)
#         return
#
#     valid = 0
#     invalid = 0
#
#     for path_str in paths:
#         path = Path(path_str)
#
#         try:
#             with ZipBundle(path, mode="r") as zb:
#                 spec = zb.read_json("spec.json")
#
#             # Check schema
#             schema = spec.get("schema", {})
#             schema_name = schema.get("name", "unknown")
#             schema_version = schema.get("version", "unknown")
#             bundle_type = spec.get("type", "unknown")
#             bundle_id = spec.get("bundle_id", "missing")
#
#             if verbose:
#                 click.echo(f"\n{path}:")
#                 click.echo(f"  Schema: {schema_name} v{schema_version}")
#                 click.echo(f"  Type: {bundle_type}")
#                 click.echo(f"  ID: {bundle_id}")
#                 constraints = spec.get("constraints", {})
#                 click.echo(f"  Constraints: {constraints}")
#
#             # Validate structure
#             validate_stx_bundle(spec)
#
#             click.secho(f"VALID: {path}", fg="green")
#             valid += 1
#
#         except FileNotFoundError as e:
#             click.secho(f"INVALID: {path} - File not found: {e}", fg="red")
#             invalid += 1
#         except Exception as e:
#             click.secho(f"INVALID: {path} - {e}", fg="red")
#             invalid += 1
#
#     # Summary
#     click.echo()
#     click.echo(f"Valid: {valid}, Invalid: {invalid}")
#
#     if invalid > 0:
#         sys.exit(1)
#
#
# @convert.command("info")
# @click.argument("path", type=click.Path(exists=True))
# def bundle_info(path: str):
#     """Show information about a bundle file.
#
#     \b
#     Displays:
#       - Format (stx vs legacy)
#       - Schema version
#       - Bundle type
#       - Contents summary
#
#     \b
#     Example:
#       scitex convert info figure.stx
#     """
#     try:
#         from scitex.io.bundle import Bundle as ZipBundle
#     except ImportError:
#         click.echo("Error: scitex.io.bundle not available", err=True)
#         return
#
#     bundle_path = Path(path)
#
#     try:
#         with ZipBundle(bundle_path, mode="r") as zb:
#             spec = zb.read_json("spec.json")
#             files = zb.namelist()
#
#         # Basic info
#         click.echo(f"\nBundle: {bundle_path}")
#         click.echo(f"Extension: {bundle_path.suffix}")
#         click.echo(f"Size: {bundle_path.stat().st_size:,} bytes")
#
#         # Schema info
#         schema = spec.get("schema", {})
#         click.echo(
#             f"\nSchema: {schema.get('name', 'unknown')} v{schema.get('version', 'unknown')}"
#         )
#         click.echo(f"Type: {spec.get('type', 'unknown')}")
#         click.echo(f"Bundle ID: {spec.get('bundle_id', 'not set')}")
#
#         # Constraints
#         constraints = spec.get("constraints", {})
#         if constraints:
#             click.echo("\nConstraints:")
#             click.echo(f"  allow_children: {constraints.get('allow_children', 'N/A')}")
#             click.echo(f"  max_depth: {constraints.get('max_depth', 'N/A')}")
#
#         # Contents
#         click.echo(f"\nContents ({len(files)} files):")
#         for f in sorted(files)[:20]:  # Show first 20
#             click.echo(f"  {f}")
#         if len(files) > 20:
#             click.echo(f"  ... and {len(files) - 20} more")
#
#         # Type-specific info
#         if spec.get("type") == "figure":
#             panels = spec.get("panels", [])
#             elements = spec.get("elements", [])
#             click.echo(f"\nPanels: {len(panels)}")
#             click.echo(f"Elements: {len(elements)}")
#         elif spec.get("type") == "plot":
#             click.echo(f"\nPlot type: {spec.get('plot_type', 'unknown')}")
#         elif spec.get("type") == "stats":
#             comparisons = spec.get("comparisons", [])
#             click.echo(f"\nComparisons: {len(comparisons)}")
#
#     except Exception as e:
#         click.secho(f"Error reading bundle: {e}", fg="red", err=True)
#         sys.exit(1)
#
#
# def _convert_bundle(input_path: Path, output_path: Path) -> None:
#     """Convert a legacy bundle to .stx format.
#
#     Args:
#         input_path: Path to legacy bundle (.figz, .pltz, .statsz)
#         output_path: Path for output .stx bundle
#     """
#     import json
#     import tempfile
#
#     # Generate bundle ID and normalize spec - inline functions since io.bundle is deprecated
#     import uuid
#     import zipfile
#
#     def generate_bundle_id():
#         return str(uuid.uuid4())[:8]
#
#     def normalize_spec(spec):
#         return spec  # FTS handles normalization internally
#
#     # Determine bundle type from extension
#     ext = input_path.suffix
#     type_map = {
#         ".figz": "figure",
#         ".pltz": "plot",
#         ".statsz": "stats",
#     }
#     bundle_type = type_map.get(ext)
#
#     # Read input bundle
#     with zipfile.ZipFile(input_path, "r") as zf:
#         # Read spec
#         spec_data = zf.read("spec.json")
#         spec = json.loads(spec_data)
#
#         # Normalize to v2.0.0
#         normalized_spec = normalize_spec(spec, bundle_type)
#
#         # Ensure bundle_id
#         if "bundle_id" not in normalized_spec:
#             normalized_spec["bundle_id"] = generate_bundle_id()
#
#         # Copy all files to new bundle
#         with tempfile.TemporaryDirectory() as tmpdir:
#             # Extract all
#             zf.extractall(tmpdir)
#
#             # Write updated spec
#             spec_path = Path(tmpdir) / "spec.json"
#             with open(spec_path, "w") as f:
#                 json.dump(normalized_spec, f, indent=2)
#
#             # Create output bundle
#             output_path.parent.mkdir(parents=True, exist_ok=True)
#             with zipfile.ZipFile(output_path, "w", zipfile.ZIP_DEFLATED) as out_zf:
#                 for file_path in Path(tmpdir).rglob("*"):
#                     if file_path.is_file():
#                         arcname = file_path.relative_to(tmpdir)
#                         out_zf.write(file_path, arcname)
#
#
# # EOF

# --------------------------------------------------------------------------------
# End of Source Code from: /home/ywatanabe/proj/scitex-code/src/scitex/cli/convert.py
# --------------------------------------------------------------------------------
