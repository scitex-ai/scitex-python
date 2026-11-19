#!/usr/bin/env python3
"""SciTeX Skills CLI — Browse skills across the entire ecosystem.

Since scitex is the orchestrator, 'scitex skills' aggregates all packages.
The skill registry lives in scitex-dev (``scitex_dev.ecosystem``).
"""

import json
from pathlib import Path

import click


@click.group(invoke_without_command=True)
@click.pass_context
def skills(ctx):
    """View skills across the entire SciTeX ecosystem.

    \b
    Examples:
      scitex skills list
      scitex skills get scitex-stats
      scitex skills install --dry-run
    """
    if ctx.invoked_subcommand is None:
        click.echo(ctx.get_help())


@skills.command("list")
@click.option("--json", "as_json", is_flag=True, help="JSON output")
def skills_list(as_json):
    """List all skill pages across the ecosystem.

    \b
    Examples:
      scitex skills list
      scitex skills list --json
    """
    from scitex_dev.ecosystem import list_skills

    all_skills = list_skills()

    if as_json:
        click.echo(json.dumps(all_skills, indent=2, default=str))
        return

    for pkg, entries in sorted(all_skills.items()):
        click.secho(f"\n{pkg}:", fg="cyan", bold=True)
        for entry in entries:
            name = entry.get("name", "SKILL")
            desc = entry.get("description", "")
            click.echo(f"  {name}")
            if desc:
                click.echo(f"    {desc}")

    click.echo()
    click.echo("Usage: scitex skills get <package> [name]")


@skills.command("get")
@click.argument("target", required=False, default=None)
@click.argument("name", required=False, default=None)
@click.option(
    "--json", "as_json", is_flag=True, help="Output {package, name, content} as JSON"
)
def skills_get(target, name, as_json):
    """Show a skill page.

    \b
    Examples:
      scitex skills get all              # All SKILL.md files concatenated
      scitex skills get scitex-stats     # Main SKILL.md for scitex-stats
      scitex skills get scitex-stats test-selection  # Specific reference
      scitex skills get scitex-stats --json
    """
    from scitex_dev.ecosystem import get_skill, list_skills

    if target is None or target == "all":
        all_skills = list_skills()
        pages = []
        for pkg, entries in sorted(all_skills.items()):
            for entry in entries:
                skill_name = entry["name"] if entry["name"] != "SKILL" else None
                content = get_skill(package=pkg, name=skill_name)
                if content:
                    pages.append(
                        {"package": pkg, "name": entry["name"], "content": content}
                    )
        if as_json:
            click.echo(json.dumps(pages, indent=2))
            return
        for page in pages:
            click.secho(f"\n{'=' * 60}", fg="cyan")
            click.secho(f"  {page['package']}/{page['name']}", fg="cyan", bold=True)
            click.secho(f"{'=' * 60}", fg="cyan")
            click.echo(page["content"])
        return

    content = get_skill(package=target, name=name)
    if content:
        if as_json:
            click.echo(
                json.dumps(
                    {"package": target, "name": name or "SKILL", "content": content}
                )
            )
        else:
            click.echo(content)
        return

    available = list_skills()
    missing = f"Skill not found: {target}" + (f"/{name}" if name else "")
    if as_json:
        click.echo(json.dumps({"error": missing, "available": sorted(available)}))
        raise SystemExit(1)
    click.secho(missing, fg="red")
    if target in available:
        click.echo(f"\nAvailable for {target}:")
        for entry in available[target]:
            click.echo(f"  {entry.get('name', 'SKILL')}")
    else:
        click.echo(f"\nAvailable packages: {', '.join(sorted(available.keys()))}")
    raise SystemExit(1)


#: Same variable and default as scitex-dev's own `skills export`.
_DEST_ENV = "SCITEX_DEV_SKILLS_DEFAULT_EXPORT_DIR"


def _default_dest() -> Path:
    """Default install destination: ``$SCITEX_DEV_SKILLS_DEFAULT_EXPORT_DIR``."""
    import os

    env = os.environ.get(_DEST_ENV)
    return Path(env) if env else Path.home() / ".claude" / "skills" / "scitex"


def _install(dest, package, clean, dry_run, as_json):
    """Install (export) ecosystem skills into ``dest``; shared by both verbs."""
    from scitex_dev.ecosystem import export_skills, list_skills

    target = Path(dest).expanduser() if dest else _default_dest()

    if dry_run:
        planned = {
            pkg: [entry["name"] for entry in entries]
            for pkg, entries in sorted(list_skills(package=package).items())
        }
        if as_json:
            click.echo(json.dumps({"dest": str(target), "packages": planned}))
            return
        total = sum(len(names) for names in planned.values())
        click.echo(f"[dry-run] Would install {total} skill pages into {target}")
        for pkg, names in planned.items():
            click.echo(f"  {pkg}: {len(names)} page(s)")
        return

    exported = export_skills(target, package=package, clean=clean)
    if as_json:
        click.echo(
            json.dumps(
                {
                    "dest": str(target),
                    "packages": {k: [str(f) for f in v] for k, v in exported.items()},
                }
            )
        )
        return
    if not exported:
        click.secho("No skills found to install.", fg="yellow")
        return
    total = 0
    for pkg_name, files in sorted(exported.items()):
        click.secho(f"  {pkg_name}/", fg="cyan")
        for f in files:
            click.echo(f"    {f}")
            total += 1
    click.echo()
    click.secho(f"Installed {total} files into {target}", fg="green")


_DEST_HELP = (
    "Destination directory "
    "(default: $SCITEX_DEV_SKILLS_DEFAULT_EXPORT_DIR or ~/.claude/skills/scitex/)."
)


@skills.command("install")
@click.option("--dest", type=click.Path(), default=None, help=_DEST_HELP)
@click.option("--package", default=None, help="Install only this package.")
@click.option("--clean", is_flag=True, help="Replace each package's directory.")
@click.option("--dry-run", is_flag=True, help="List what would be installed.")
@click.option(
    "--yes",
    "-y",
    is_flag=True,
    help="Skip confirmation (install never prompts; accepted for scripts).",
)
@click.option("--json", "as_json", is_flag=True, help="Output as JSON")
def skills_install(dest, package, clean, dry_run, yes, as_json):
    """Install ecosystem skills for Claude Code discovery.

    \b
    Examples:
      scitex skills install                       # All packages, default dest
      scitex skills install --package scitex-stats
      scitex skills install --dest /tmp/skills --dry-run
    """
    del yes  # installation writes only under --dest; nothing to confirm
    _install(dest, package, clean, dry_run, as_json)


@skills.command("export")
@click.option("--dest", type=click.Path(), default=None, help=_DEST_HELP)
@click.option("--package", default=None, help="Export only this package.")
@click.option("--clean", is_flag=True, help="Replace each package's directory.")
@click.option("--dry-run", is_flag=True, help="List what would be exported.")
@click.option(
    "--yes",
    "-y",
    is_flag=True,
    help="Skip confirmation (export never prompts; accepted for scripts).",
)
@click.option("--json", "as_json", is_flag=True, help="Output as JSON")
def skills_export(dest, package, clean, dry_run, yes, as_json):
    """Export skills for Claude Code discovery (same as `install`).

    \b
    Examples:
      scitex skills export                     # Export all packages
      scitex skills export --package scitex-stats
      scitex skills export --dest /tmp/skills  # Custom destination
      scitex skills export --dry-run --json    # Preview
    """
    del yes  # export writes only under --dest; nothing to confirm
    _install(dest, package, clean, dry_run, as_json)
