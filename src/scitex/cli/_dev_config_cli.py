#!/usr/bin/env python3
# Timestamp: 2026-03-11
# File: scitex/cli/_dev_config_cli.py

"""CLI subcommand group: scitex dev config."""

import click


@click.group(invoke_without_command=True)
@click.pass_context
def config(ctx):
    r"""
    Manage configuration.

    \b
    Commands:
      show     - Show current configuration
      validate - Validate configuration file
      create   - Create default config file

    \b
    Examples:
      scitex dev config show
      scitex dev config create
    """
    if ctx.invoked_subcommand is None:
        click.echo(ctx.get_help())


@config.command("show")
@click.option("--json", "as_json", is_flag=True, help="Output as JSON")
def config_show(as_json):
    """Show current configuration."""
    import json as json_module

    from scitex._dev import get_config_path, load_config

    config_path = get_config_path()
    cfg = load_config()

    if as_json:
        data = {
            "config_path": str(config_path),
            "exists": config_path.exists(),
            "packages": [p.name for p in cfg.packages],
            "hosts": [{"name": h.name, "enabled": h.enabled} for h in cfg.hosts],
            "remotes": [
                {"name": r.name, "enabled": r.enabled} for r in cfg.github_remotes
            ],
            "branches": cfg.branches,
        }
        click.echo(json_module.dumps(data, indent=2))
        return

    click.secho("Configuration", fg="cyan", bold=True)
    click.echo(f"  Path: {config_path}")
    click.echo(f"  Exists: {config_path.exists()}")
    click.echo()
    click.secho("Packages:", fg="yellow")
    for p in cfg.packages:
        click.echo(f"  - {p.name} ({p.pypi_name})")
    click.echo()
    click.secho("Hosts:", fg="yellow")
    for h in cfg.hosts:
        status = "enabled" if h.enabled else "disabled"
        click.echo(f"  - {h.name} ({h.hostname}) [{status}]")
    click.echo()
    click.secho("GitHub Remotes:", fg="yellow")
    for r in cfg.github_remotes:
        status = "enabled" if r.enabled else "disabled"
        click.echo(f"  - {r.name} (org: {r.org}) [{status}]")


@config.command("create")
@click.option("--force", is_flag=True, help="Overwrite existing config")
def config_create(force):
    """Create default configuration file."""
    from scitex._dev import create_default_config, get_config_path

    config_path = get_config_path()
    if config_path.exists() and not force:
        click.secho(f"Config already exists: {config_path}", fg="yellow")
        click.echo("Use --force to overwrite.")
        return

    path = create_default_config()
    click.secho(f"Created config: {path}", fg="green")


@config.command("validate")
def config_validate():
    """Validate configuration file."""
    import sys

    from scitex._dev import get_config_path, load_config

    config_path = get_config_path()
    if not config_path.exists():
        click.secho(f"Config not found: {config_path}", fg="red")
        click.echo("Run 'scitex dev config create' to create one.")
        sys.exit(1)

    try:
        cfg = load_config()
        click.secho("Configuration is valid.", fg="green")
        click.echo(f"  Packages: {len(cfg.packages)}")
        click.echo(f"  Hosts: {len(cfg.hosts)}")
        click.echo(f"  Remotes: {len(cfg.github_remotes)}")
    except Exception as e:
        click.secho(f"Configuration error: {e}", fg="red")
        sys.exit(1)


# EOF
