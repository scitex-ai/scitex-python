#!/usr/bin/env python3
"""Container management CLI (Apptainer/Singularity)."""

from __future__ import annotations

import click


@click.group(invoke_without_command=True)
@click.option(
    "--json",
    "as_json",
    is_flag=True,
    help="Output as structured JSON (Result envelope).",
)
@click.pass_context
def container(ctx, as_json):
    """Container management (Apptainer/Singularity)."""
    if ctx.invoked_subcommand is None:
        if as_json:
            from . import group_to_json

            group_to_json(ctx, container)
        else:
            click.echo(ctx.get_help())


@container.command()
@click.argument("name", default="scitex-cloud-shared-v0.1.0")
@click.option("--force", "-f", is_flag=True, help="Force rebuild.")
@click.option("--output-dir", "-o", type=click.Path(), help="Output directory.")
@click.option(
    "--base", is_flag=True, help="Build the base image instead of the final image."
)
def build(name, force, output_dir, base):
    """Build a SciTeX container from .def file."""
    from scitex.container import build as do_build

    if base:
        name = name.replace("final", "base")
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
    """List available container versions."""
    from pathlib import Path

    from scitex.container import find_containers_dir, get_active_version, list_versions

    try:
        cdir = Path(containers_dir) if containers_dir else find_containers_dir()
    except FileNotFoundError as e:
        click.secho(str(e), fg="red", err=True)
        raise SystemExit(1)

    versions = list_versions(cdir)
    if not versions:
        click.echo(f"No versioned SIFs in {cdir}")
        return

    active = get_active_version(cdir)
    click.secho(f"Container versions in {cdir}:", fg="cyan")
    for v in versions:
        marker = click.style(" *", fg="green") if v["active"] else "  "
        version_str = click.style(v["version"], fg="green" if v["active"] else "white")
        click.echo(f"  {marker} {version_str}  {v['size']}  {v['date']}")

    if active:
        click.echo()
        click.echo(f"  Active: {click.style(active, fg='green', bold=True)}")


@container.command()
@click.argument("version")
@click.option(
    "--dir", "-d", "containers_dir", type=click.Path(), help="Containers directory."
)
@click.option("--sudo", is_flag=True, help="Use sudo for symlink operations.")
def switch(version, containers_dir, sudo):
    """Switch active container to VERSION."""
    from pathlib import Path

    from scitex.container import find_containers_dir, get_active_version, switch_version

    try:
        cdir = Path(containers_dir) if containers_dir else find_containers_dir()
    except FileNotFoundError as e:
        click.secho(str(e), fg="red", err=True)
        raise SystemExit(1)

    old_version = get_active_version(cdir)

    try:
        switch_version(version, cdir, use_sudo=sudo)
    except FileNotFoundError as e:
        click.secho(str(e), fg="red", err=True)
        raise SystemExit(1)
    except RuntimeError as e:
        click.secho(f"Switch failed: {e}", fg="red", err=True)
        raise SystemExit(1)

    if old_version:
        click.secho(f"Switched {old_version} -> {version}", fg="green")
    else:
        click.secho(f"Activated version {version}", fg="green")


@container.command()
@click.option(
    "--dir", "-d", "containers_dir", type=click.Path(), help="Containers directory."
)
@click.option("--sudo", is_flag=True, help="Use sudo for symlink operations.")
def rollback(containers_dir, sudo):
    """Revert to the previous container version."""
    from pathlib import Path

    from scitex.container import find_containers_dir, get_active_version
    from scitex.container import rollback as do_rollback

    try:
        cdir = Path(containers_dir) if containers_dir else find_containers_dir()
    except FileNotFoundError as e:
        click.secho(str(e), fg="red", err=True)
        raise SystemExit(1)

    old_version = get_active_version(cdir)

    try:
        new_version = do_rollback(cdir, use_sudo=sudo)
    except RuntimeError as e:
        click.secho(f"Rollback failed: {e}", fg="red", err=True)
        raise SystemExit(1)

    click.secho(f"Rolled back {old_version} -> {new_version}", fg="green")


@container.command()
@click.option(
    "--target",
    "-t",
    "target_dir",
    type=click.Path(),
    default="/opt/scitex/singularity",
    show_default=True,
    help="Deployment target directory.",
)
@click.option(
    "--dir",
    "-d",
    "containers_dir",
    type=click.Path(),
    help="Source containers directory.",
)
def deploy(target_dir, containers_dir):
    """Copy active SIF to production target directory."""
    from pathlib import Path

    from scitex.container import deploy as do_deploy
    from scitex.container import find_containers_dir

    try:
        cdir = Path(containers_dir) if containers_dir else find_containers_dir()
    except FileNotFoundError as e:
        click.secho(str(e), fg="red", err=True)
        raise SystemExit(1)

    try:
        do_deploy(source_dir=cdir, target_dir=Path(target_dir))
    except (FileNotFoundError, RuntimeError) as e:
        click.secho(f"Deploy failed: {e}", fg="red", err=True)
        raise SystemExit(1)

    click.secho(f"Deployed to {target_dir}", fg="green")


@container.command()
@click.option(
    "--keep",
    "-k",
    type=int,
    default=3,
    show_default=True,
    help="Number of recent versions to keep.",
)
@click.option(
    "--dir", "-d", "containers_dir", type=click.Path(), help="Containers directory."
)
def cleanup(keep, containers_dir):
    """Remove old container versions, keeping the N most recent."""
    from pathlib import Path

    from scitex.container import cleanup as do_cleanup
    from scitex.container import find_containers_dir

    try:
        cdir = Path(containers_dir) if containers_dir else find_containers_dir()
    except FileNotFoundError as e:
        click.secho(str(e), fg="red", err=True)
        raise SystemExit(1)

    removed = do_cleanup(cdir, keep=keep)

    if removed:
        click.secho(f"Removed {len(removed)} old version(s):", fg="yellow")
        for path in removed:
            click.echo(f"  {path.name}")
    else:
        click.secho("No versions to remove.", fg="green")


# EOF
