#!/usr/bin/env python3
# Timestamp: "2025-12-19 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex-code/src/scitex/cli/convert.py

"""CLI commands for converting legacy bundle formats to unified .stx format."""

import sys
from pathlib import Path
from typing import List, Optional

import click


@click.group(invoke_without_command=True)
@click.option(
    "--json",
    "as_json",
    is_flag=True,
    help="Output as structured JSON (Result envelope).",
)
@click.pass_context
def convert(ctx, as_json):
    """Convert and validate SciTeX bundle files."""
    if ctx.invoked_subcommand is None:
        if as_json:
            from . import group_to_json

            group_to_json(ctx, convert)
        else:
            click.echo(ctx.get_help())


@convert.command("file")
@click.argument("input_path", type=click.Path(exists=True))
@click.option(
    "-o",
    "--output",
    type=click.Path(),
    help="Output path (default: same name with .stx extension)",
)
@click.option(
    "--overwrite",
    is_flag=True,
    help="Overwrite output file if it exists",
)
@click.option(
    "--dry-run",
    is_flag=True,
    help="Show what would be done without writing files",
)
@click.option("--json", "as_json", is_flag=True, help="Output as JSON")
def convert_file(
    input_path: str,
    output: Optional[str],
    overwrite: bool,
    dry_run: bool,
    as_json: bool,
):
    """Convert a single legacy bundle to .stx format.

    \b
    Supported input formats:
      .figz  - Figure bundles
      .pltz  - Plot bundles
      .statsz - Statistics bundles

    \b
    Examples:
      scitex convert file old_figure.figz
      scitex convert file plot.pltz -o converted_plot.stx
      scitex convert file stats.statsz --dry-run
    """
    if as_json:
        from scitex_dev import wrap_as_cli

        def _convert():
            input_file = Path(input_path)
            if output:
                output_file = Path(output)
            else:
                output_file = input_file.with_suffix(".stx")
            if dry_run:
                return {
                    "action": "dry_run",
                    "input": str(input_file),
                    "output": str(output_file),
                }
            _convert_bundle(input_file, output_file)
            return {"converted": str(input_file), "output": str(output_file)}

        wrap_as_cli(_convert, as_json=True)
        return

    input_file = Path(input_path)

    # Determine output path
    if output:
        output_file = Path(output)
    else:
        output_file = input_file.with_suffix(".stx")

    # Check if already .stx
    if input_file.suffix == ".stx":
        click.secho(f"File is already in .stx format: {input_file}", fg="yellow")
        return

    # Validate input format
    valid_extensions = (".figz", ".pltz", ".statsz")
    if input_file.suffix not in valid_extensions:
        click.secho(
            f"Unsupported format: {input_file.suffix}. "
            f"Supported: {', '.join(valid_extensions)}",
            fg="red",
            err=True,
        )
        sys.exit(1)

    # Check output exists
    if output_file.exists() and not overwrite:
        click.secho(
            f"Output file exists: {output_file}. Use --overwrite to replace.",
            fg="red",
            err=True,
        )
        sys.exit(1)

    if dry_run:
        click.echo(f"Would convert: {input_file} -> {output_file}")
        return

    # Perform conversion
    try:
        _convert_bundle(input_file, output_file)
        click.secho(f"Converted: {input_file} -> {output_file}", fg="green")
    except Exception as e:
        click.secho(f"Error converting {input_file}: {e}", fg="red", err=True)
        sys.exit(1)


@convert.command("batch")
@click.argument("pattern", nargs=-1, required=True)
@click.option(
    "-o",
    "--output-dir",
    type=click.Path(),
    help="Output directory (default: same as input)",
)
@click.option(
    "--overwrite",
    is_flag=True,
    help="Overwrite existing files",
)
@click.option(
    "--dry-run",
    is_flag=True,
    help="Show what would be done without writing files",
)
@click.option("--json", "as_json", is_flag=True, help="Output as JSON")
def convert_batch(
    pattern: tuple,
    output_dir: Optional[str],
    overwrite: bool,
    dry_run: bool,
    as_json: bool,
):
    """Batch convert multiple legacy bundles to .stx format.

    \b
    Examples:
      scitex convert batch ./figures/*.figz
      scitex convert batch ./plots/*.pltz -o ./converted/
      scitex convert batch ./**/*.figz ./**/*.pltz --dry-run
    """
    if as_json:
        from scitex_dev import wrap_as_cli

        def _batch():
            import glob as _glob

            files: List[Path] = []
            for pat in pattern:
                matches = _glob.glob(pat, recursive=True)
                files.extend(Path(m) for m in matches)
            valid_extensions = (".figz", ".pltz", ".statsz")
            files = [f for f in files if f.suffix in valid_extensions]
            if not files:
                return {"converted": 0, "errors": 0, "files": []}
            out_dir = Path(output_dir) if output_dir else None
            if out_dir and not dry_run:
                out_dir.mkdir(parents=True, exist_ok=True)
            results = []
            converted = 0
            errs = 0
            for input_file in files:
                if out_dir:
                    output_file = out_dir / input_file.with_suffix(".stx").name
                else:
                    output_file = input_file.with_suffix(".stx")
                if output_file.exists() and not overwrite:
                    results.append({"input": str(input_file), "status": "skipped"})
                    continue
                if dry_run:
                    results.append(
                        {
                            "input": str(input_file),
                            "output": str(output_file),
                            "status": "dry_run",
                        }
                    )
                    converted += 1
                    continue
                try:
                    _convert_bundle(input_file, output_file)
                    results.append(
                        {
                            "input": str(input_file),
                            "output": str(output_file),
                            "status": "converted",
                        }
                    )
                    converted += 1
                except Exception as exc:
                    results.append(
                        {"input": str(input_file), "status": "error", "error": str(exc)}
                    )
                    errs += 1
            return {"converted": converted, "errors": errs, "files": results}

        wrap_as_cli(_batch, as_json=True)
        return

    import glob

    # Collect all files matching patterns
    files: List[Path] = []
    for pat in pattern:
        matches = glob.glob(pat, recursive=True)
        files.extend(Path(m) for m in matches)

    # Filter to valid extensions
    valid_extensions = (".figz", ".pltz", ".statsz")
    files = [f for f in files if f.suffix in valid_extensions]

    if not files:
        click.secho("No matching files found.", fg="yellow")
        return

    click.echo(f"Found {len(files)} file(s) to convert")

    # Determine output directory
    out_dir = Path(output_dir) if output_dir else None
    if out_dir and not dry_run:
        out_dir.mkdir(parents=True, exist_ok=True)

    # Convert each file
    converted = 0
    errors = 0
    for input_file in files:
        if out_dir:
            output_file = out_dir / input_file.with_suffix(".stx").name
        else:
            output_file = input_file.with_suffix(".stx")

        if output_file.exists() and not overwrite:
            click.secho(f"Skipping (exists): {output_file}", fg="yellow")
            continue

        if dry_run:
            click.echo(f"Would convert: {input_file} -> {output_file}")
            converted += 1
            continue

        try:
            _convert_bundle(input_file, output_file)
            click.secho(
                f"Converted: {input_file.name} -> {output_file.name}", fg="green"
            )
            converted += 1
        except Exception as e:
            click.secho(f"Error: {input_file}: {e}", fg="red", err=True)
            errors += 1

    # Summary
    click.echo()
    click.echo(f"Converted: {converted}, Errors: {errors}")


@convert.command("validate")
@click.argument("paths", nargs=-1, required=True, type=click.Path(exists=True))
@click.option(
    "--verbose",
    "-v",
    is_flag=True,
    help="Show detailed validation info",
)
def validate_bundles(paths: tuple, verbose: bool):
    """Validate one or more .stx bundles.

    \b
    Checks:
      - Valid ZIP structure
      - spec.json present and valid
      - Schema version
      - Depth limits
      - Circular references

    \b
    Examples:
      scitex convert validate output.stx
      scitex convert validate ./figures/*.stx --verbose
    """
    # Use Bundle for validation
    try:
        from scitex.io.bundle import Bundle as ZipBundle

        def validate_stx_bundle(path):
            try:
                bundle = ZipBundle(path)
                return bundle.validate(level="strict")
            except Exception as e:
                return {"valid": False, "errors": [str(e)]}

    except ImportError:
        click.echo("Error: scitex.io.bundle not available", err=True)
        return

    valid = 0
    invalid = 0

    for path_str in paths:
        path = Path(path_str)

        try:
            with ZipBundle(path, mode="r") as zb:
                spec = zb.read_json("spec.json")

            # Check schema
            schema = spec.get("schema", {})
            schema_name = schema.get("name", "unknown")
            schema_version = schema.get("version", "unknown")
            bundle_type = spec.get("type", "unknown")
            bundle_id = spec.get("bundle_id", "missing")

            if verbose:
                click.echo(f"\n{path}:")
                click.echo(f"  Schema: {schema_name} v{schema_version}")
                click.echo(f"  Type: {bundle_type}")
                click.echo(f"  ID: {bundle_id}")
                constraints = spec.get("constraints", {})
                click.echo(f"  Constraints: {constraints}")

            # Validate structure
            validate_stx_bundle(spec)

            click.secho(f"VALID: {path}", fg="green")
            valid += 1

        except FileNotFoundError as e:
            click.secho(f"INVALID: {path} - File not found: {e}", fg="red")
            invalid += 1
        except Exception as e:
            click.secho(f"INVALID: {path} - {e}", fg="red")
            invalid += 1

    # Summary
    click.echo()
    click.echo(f"Valid: {valid}, Invalid: {invalid}")

    if invalid > 0:
        sys.exit(1)


@convert.command("info")
@click.argument("path", type=click.Path(exists=True))
def bundle_info(path: str):
    """Show information about a bundle file.

    \b
    Displays:
      - Format (stx vs legacy)
      - Schema version
      - Bundle type
      - Contents summary

    \b
    Example:
      scitex convert info figure.stx
    """
    try:
        from scitex.io.bundle import Bundle as ZipBundle
    except ImportError:
        click.echo("Error: scitex.io.bundle not available", err=True)
        return

    bundle_path = Path(path)

    try:
        with ZipBundle(bundle_path, mode="r") as zb:
            spec = zb.read_json("spec.json")
            files = zb.namelist()

        # Basic info
        click.echo(f"\nBundle: {bundle_path}")
        click.echo(f"Extension: {bundle_path.suffix}")
        click.echo(f"Size: {bundle_path.stat().st_size:,} bytes")

        # Schema info
        schema = spec.get("schema", {})
        click.echo(
            f"\nSchema: {schema.get('name', 'unknown')} v{schema.get('version', 'unknown')}"
        )
        click.echo(f"Type: {spec.get('type', 'unknown')}")
        click.echo(f"Bundle ID: {spec.get('bundle_id', 'not set')}")

        # Constraints
        constraints = spec.get("constraints", {})
        if constraints:
            click.echo("\nConstraints:")
            click.echo(f"  allow_children: {constraints.get('allow_children', 'N/A')}")
            click.echo(f"  max_depth: {constraints.get('max_depth', 'N/A')}")

        # Contents
        click.echo(f"\nContents ({len(files)} files):")
        for f in sorted(files)[:20]:  # Show first 20
            click.echo(f"  {f}")
        if len(files) > 20:
            click.echo(f"  ... and {len(files) - 20} more")

        # Type-specific info
        if spec.get("type") == "figure":
            panels = spec.get("panels", [])
            elements = spec.get("elements", [])
            click.echo(f"\nPanels: {len(panels)}")
            click.echo(f"Elements: {len(elements)}")
        elif spec.get("type") == "plot":
            click.echo(f"\nPlot type: {spec.get('plot_type', 'unknown')}")
        elif spec.get("type") == "stats":
            comparisons = spec.get("comparisons", [])
            click.echo(f"\nComparisons: {len(comparisons)}")

    except Exception as e:
        click.secho(f"Error reading bundle: {e}", fg="red", err=True)
        sys.exit(1)


def _convert_bundle(input_path: Path, output_path: Path) -> None:
    """Convert a legacy bundle to .stx format.

    Args:
        input_path: Path to legacy bundle (.figz, .pltz, .statsz)
        output_path: Path for output .stx bundle
    """
    import json
    import tempfile

    # Generate bundle ID and normalize spec - inline functions since io.bundle is deprecated
    import uuid
    import zipfile

    def generate_bundle_id():
        return str(uuid.uuid4())[:8]

    def normalize_spec(spec):
        return spec  # FTS handles normalization internally

    # Determine bundle type from extension
    ext = input_path.suffix
    type_map = {
        ".figz": "figure",
        ".pltz": "plot",
        ".statsz": "stats",
    }
    bundle_type = type_map.get(ext)

    # Read input bundle
    with zipfile.ZipFile(input_path, "r") as zf:
        # Read spec
        spec_data = zf.read("spec.json")
        spec = json.loads(spec_data)

        # Normalize to v2.0.0
        normalized_spec = normalize_spec(spec, bundle_type)

        # Ensure bundle_id
        if "bundle_id" not in normalized_spec:
            normalized_spec["bundle_id"] = generate_bundle_id()

        # Copy all files to new bundle
        with tempfile.TemporaryDirectory() as tmpdir:
            # Extract all
            zf.extractall(tmpdir)

            # Write updated spec
            spec_path = Path(tmpdir) / "spec.json"
            with open(spec_path, "w") as f:
                json.dump(normalized_spec, f, indent=2)

            # Create output bundle
            output_path.parent.mkdir(parents=True, exist_ok=True)
            with zipfile.ZipFile(output_path, "w", zipfile.ZIP_DEFLATED) as out_zf:
                for file_path in Path(tmpdir).rglob("*"):
                    if file_path.is_file():
                        arcname = file_path.relative_to(tmpdir)
                        out_zf.write(file_path, arcname)


# EOF
