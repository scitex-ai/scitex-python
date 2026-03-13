#!/usr/bin/env python3
# Timestamp: "2025-12-09 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex-code/src/scitex/cli/config.py

"""
SciTeX Configuration CLI Commands

Commands for managing SciTeX configuration and paths.
"""

import os

import click


@click.group(invoke_without_command=True)
@click.option(
    "--json",
    "as_json",
    is_flag=True,
    help="Output as structured JSON (Result envelope).",
)
@click.pass_context
def config(ctx, as_json):
    """
    Configuration management commands.

    \b
    Examples:
      scitex config list          # Show all configured paths
      scitex config list --env    # Show environment variables
      scitex config init          # Initialize all directories
    """
    if ctx.invoked_subcommand is None:
        if as_json:
            from . import group_to_json

            group_to_json(ctx, config)
        else:
            click.echo(ctx.get_help())


@config.command("list")
@click.option(
    "--env",
    is_flag=True,
    help="Show relevant environment variables",
)
@click.option(
    "--exists",
    is_flag=True,
    help="Only show paths that exist",
)
@click.option(
    "--json",
    "as_json",
    is_flag=True,
    help="Output as JSON",
)
def list_config(env, exists, as_json):
    """
    List all configured paths and settings.

    \b
    Examples:
      scitex config list            # Show all paths
      scitex config list --env      # Include environment variables
      scitex config list --exists   # Only show existing directories
      scitex config list --json     # Output as JSON
    """
    from scitex.config import ScitexPaths

    paths = ScitexPaths()
    all_paths = paths.list_all()

    if as_json:
        import json

        output = {}
        if env:
            output["environment"] = {
                "SCITEX_DIR": os.getenv("SCITEX_DIR", "(not set)"),
            }
        output["paths"] = {k: str(v) for k, v in all_paths.items()}
        if exists:
            output["paths"] = {
                k: v for k, v in output["paths"].items() if all_paths[k].exists()
            }
        click.echo(json.dumps(output, indent=2))
        return

    # Header
    click.secho("SciTeX Configuration", fg="cyan", bold=True)
    click.echo("=" * 50)
    click.echo()

    # Environment variables
    if env:
        click.secho("Environment Variables:", fg="yellow", bold=True)
        scitex_dir = os.getenv("SCITEX_DIR")
        if scitex_dir:
            click.echo(f"  SCITEX_DIR = {scitex_dir}")
        else:
            click.echo("  SCITEX_DIR = (not set, using default: ~/.scitex)")
        click.echo()

    # Base directory
    click.secho("Base Directory:", fg="yellow", bold=True)
    base = paths.base
    exists_mark = (
        click.style("✓", fg="green") if base.exists() else click.style("✗", fg="red")
    )
    click.echo(f"  {exists_mark} {base}")
    click.echo()

    # All paths
    click.secho("Configured Paths:", fg="yellow", bold=True)

    # Group paths by category
    categories = {
        "Core": ["logs", "cache", "function_cache", "capture", "screenshots", "rng"],
        "Browser": [
            "browser",
            "browser_screenshots",
            "browser_sessions",
            "browser_persistent",
            "test_monitor",
        ],
        "Cache": ["impact_factor_cache", "openathens_cache"],
        "Scholar": ["scholar", "scholar_cache", "scholar_library"],
        "Other": ["writer"],
    }

    for category, path_names in categories.items():
        click.secho(f"\n  {category}:", fg="blue")
        for name in path_names:
            if name not in all_paths:
                continue
            path = all_paths[name]
            if exists and not path.exists():
                continue
            exists_mark = (
                click.style("✓", fg="green")
                if path.exists()
                else click.style("✗", fg="red")
            )
            # Show relative to base if under base
            try:
                rel_path = path.relative_to(paths.base)
                display_path = f"$SCITEX_DIR/{rel_path}"
            except ValueError:
                display_path = str(path)
            click.echo(f"    {exists_mark} {name:<22} {display_path}")

    click.echo()


@config.command("init")
@click.option(
    "--dry-run",
    is_flag=True,
    help="Show what would be created without creating",
)
def init_config(dry_run):
    """
    Initialize all SciTeX directories.

    Creates all standard directories if they don't exist.

    \b
    Examples:
      scitex config init            # Create all directories
      scitex config init --dry-run  # Show what would be created
    """
    from scitex.config import ScitexPaths

    paths = ScitexPaths()
    all_paths = paths.list_all()

    click.secho("Initializing SciTeX directories...", fg="cyan", bold=True)
    click.echo()

    created = 0
    existed = 0

    for name, path in all_paths.items():
        if path.exists():
            existed += 1
            click.echo(f"  {click.style('EXISTS', fg='yellow')}: {path}")
        else:
            if dry_run:
                click.echo(f"  {click.style('WOULD CREATE', fg='blue')}: {path}")
            else:
                path.mkdir(parents=True, exist_ok=True)
                click.echo(f"  {click.style('CREATED', fg='green')}: {path}")
            created += 1

    click.echo()
    if dry_run:
        click.echo(f"Would create {created} directories ({existed} already exist)")
    else:
        click.echo(f"Created {created} directories ({existed} already existed)")


@config.command("show")
@click.argument("path_name")
def show_path(path_name):
    """
    Show a specific configured path.

    \b
    PATH_NAME can be one of:
      base, logs, cache, function_cache, capture, screenshots,
      browser, browser_screenshots, browser_sessions, browser_persistent,
      test_monitor, impact_factor_cache, openathens_cache,
      scholar, scholar_cache, scholar_library, writer, rng

    \b
    Examples:
      scitex config show logs
      scitex config show scholar_library
    """
    from scitex.config import ScitexPaths

    paths = ScitexPaths()

    if hasattr(paths, path_name):
        path = getattr(paths, path_name)
        click.echo(str(path))
    else:
        available = list(paths.list_all().keys())
        click.secho(f"Unknown path: {path_name}", fg="red", err=True)
        click.echo(f"Available paths: {', '.join(available)}", err=True)
        raise SystemExit(1)


# EOF
