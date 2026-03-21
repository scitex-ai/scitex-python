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
        for pkg in sorted(all_skills.keys()):
            content = get_skill(package=pkg, name=None)
            if content:
                click.secho(f"{'=' * 60}", fg="cyan")
                click.secho(f"  {pkg}", fg="cyan", bold=True)
                click.secho(f"{'=' * 60}", fg="cyan")
                click.echo(content)
                click.echo()
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
