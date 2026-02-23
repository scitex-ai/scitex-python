#!/usr/bin/env python3
"""Container management CLI (Apptainer/Singularity)."""

from __future__ import annotations

import click


@click.group()
def container():
    """Container management (Apptainer/Singularity)."""


@container.command()
@click.argument("name", default="scitex-cloud-shared-v0.1.0")
@click.option("--force", "-f", is_flag=True, help="Force rebuild.")
@click.option("--output-dir", "-o", type=click.Path(), help="Output directory.")
def build(name, force, output_dir):
    """Build a SciTeX container from .def file."""
    from scitex.container import build as do_build

    try:
        sif_path = do_build(def_name=name, output_dir=output_dir, force=force)
        click.secho(f"SIF ready: {sif_path}", fg="green")
    except FileNotFoundError as e:
        click.secho(str(e), fg="red", err=True)
        raise SystemExit(1)
    except RuntimeError as e:
        click.secho(f"Build failed: {e}", fg="red", err=True)
        raise SystemExit(1)


@container.command()
@click.argument("sif_path", type=click.Path(exists=True))
@click.option("--output-dir", "-o", type=click.Path(), help="Output directory.")
def freeze(sif_path, output_dir):
    """Extract pinned versions from built SIF for reproducibility."""
    from scitex.container import freeze as do_freeze

    try:
        lock_files = do_freeze(sif_path=sif_path, output_dir=output_dir)
        click.secho("Lock files generated:", fg="green")
        for kind, path in lock_files.items():
            click.echo(f"  {kind}: {path}")
    except FileNotFoundError as e:
        click.secho(str(e), fg="red", err=True)
        raise SystemExit(1)


@container.command()
@click.option(
    "--dir", "-d", "containers_dir", type=click.Path(), help="Containers directory."
)
def status(containers_dir):
    """Show container status (available .def files, built SIFs, staleness)."""
    from scitex.container import status as do_status

    try:
        containers = do_status(containers_dir=containers_dir)
    except FileNotFoundError as e:
        click.secho(str(e), fg="red", err=True)
        raise SystemExit(1)

    if not containers:
        click.echo("No container definitions found.")
        return

    for c in containers:
        name = c["name"]
        if c["sif_path"]:
            if c["needs_rebuild"]:
                badge = click.style("STALE", fg="yellow")
            else:
                badge = click.style("OK", fg="green")
            click.echo(f"  {badge}  {name}  ({c['sif_size']}, built {c['sif_date']})")
        else:
            badge = click.style("NOT BUILT", fg="red")
            click.echo(f"  {badge}  {name}")


@container.command(name="list")
@click.option(
    "--dir", "-d", "containers_dir", type=click.Path(), help="Containers directory."
)
def list_containers(containers_dir):
    """List available container definitions."""
    from pathlib import Path

    from scitex.container._utils import find_containers_dir

    try:
        cdir = Path(containers_dir) if containers_dir else find_containers_dir()
    except FileNotFoundError as e:
        click.secho(str(e), fg="red", err=True)
        raise SystemExit(1)

    defs = sorted(cdir.glob("*.def"))
    if not defs:
        click.echo(f"No .def files in {cdir}")
        return

    click.secho(f"Container definitions in {cdir}:", fg="cyan")
    for d in defs:
        click.echo(f"  {d.stem}")


# EOF
