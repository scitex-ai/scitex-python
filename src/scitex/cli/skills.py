#!/usr/bin/env python3
"""SciTeX Skills CLI — Browse skills across the entire ecosystem.

Since scitex is the orchestrator, 'scitex skills' aggregates all packages.
"""

import click


@click.group(invoke_without_command=True)
@click.pass_context
def skills(ctx):
    """View skills across the entire SciTeX ecosystem."""
    if ctx.invoked_subcommand is None:
        click.echo(ctx.get_help())


@skills.command("list")
@click.option("--json", "as_json", is_flag=True, help="JSON output")
def skills_list(as_json):
    """List all skill pages across the ecosystem."""
    from scitex_dev.skills import list_skills

    all_skills = list_skills()

    if as_json:
        import json

        click.echo(json.dumps(all_skills, indent=2))
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
def skills_get(target, name):
    """Show a skill page.

    \b
    Examples:
      scitex skills get all              # All SKILL.md files concatenated
      scitex skills get scitex-stats     # Main SKILL.md for scitex-stats
      scitex skills get scitex-stats test-selection  # Specific reference
    """
    from scitex_dev.skills import get_skill, list_skills

    if target is None or target == "all":
        all_skills = list_skills()
        for pkg, entries in sorted(all_skills.items()):
            for entry in entries:
                skill_name = entry["name"] if entry["name"] != "SKILL" else None
                content = get_skill(package=pkg, name=skill_name)
                if content:
                    click.secho(f"\n{'=' * 60}", fg="cyan")
                    click.secho(f"  {pkg}/{entry['name']}", fg="cyan", bold=True)
                    click.secho(f"{'=' * 60}", fg="cyan")
                    click.echo(content)
        return

    content = get_skill(package=target, name=name)
    if content:
        click.echo(content)
    else:
        available = list_skills()
        click.secho(
            f"Skill not found: {target}" + (f"/{name}" if name else ""), fg="red"
        )
        if target in available:
            click.echo(f"\nAvailable for {target}:")
            for entry in available[target]:
                click.echo(f"  {entry.get('name', 'SKILL')}")
        else:
            click.echo(f"\nAvailable packages: {', '.join(sorted(available.keys()))}")


@skills.command("export")
@click.option(
    "--dest",
    type=click.Path(),
    default=None,
    help="Destination directory (default: .claude/skills/)",
)
@click.option("--package", default=None, help="Export only this package.")
@click.option("--clean", is_flag=True, help="Remove destination before exporting.")
def skills_export(dest, package, clean):
    """Export skills to .claude/skills/ for Claude Code discovery.

    \b
    Examples:
      scitex skills export                     # Export all to .claude/skills/
      scitex skills export --package scitex-stats
      scitex skills export --dest /tmp/skills  # Custom destination
      scitex skills export --clean             # Clean export
    """
    from pathlib import Path

    from scitex_dev.skills import export_skills

    dest_path = Path(dest) if dest else None
    mode = "upgrade" if clean else "export"
    exported = export_skills(dest=dest_path, package=package, mode=mode)

    if not exported:
        click.secho("No skills found to export.", fg="yellow")
        return

    total = 0
    for pkg_name, files in sorted(exported.items()):
        click.secho(f"  {pkg_name}/", fg="cyan")
        for f in files:
            click.echo(f"    {f}")
            total += 1

    target = dest_path or Path(".claude/skills/")
    click.echo()
    click.secho(f"Exported {total} files to {target}", fg="green")
