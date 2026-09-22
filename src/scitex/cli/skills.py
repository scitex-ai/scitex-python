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
    """List all skill pages across the ecosystem.

    Example:
      $ scitex skills list --json
    """
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
@click.option("--json", "as_json", is_flag=True, help="JSON output")
def skills_get(target, name, as_json):
    """Show a skill page.

    \b
    Examples:
      scitex skills get all              # All SKILL.md files concatenated
      scitex skills get scitex-stats     # Main SKILL.md for scitex-stats
      scitex skills get scitex-stats test-selection  # Specific reference
      $ scitex skills get scitex --json
    """
    from scitex_dev.skills import get_skill, list_skills

    if as_json:
        import json

        payload = []
        if target is None or target == "all":
            for pkg, entries in sorted(list_skills().items()):
                for entry in entries:
                    skill_name = entry["name"] if entry["name"] != "SKILL" else None
                    payload.append(
                        {
                            "package": pkg,
                            "name": entry["name"],
                            "content": get_skill(package=pkg, name=skill_name),
                        }
                    )
        else:
            payload.append(
                {
                    "package": target,
                    "name": name,
                    "content": get_skill(package=target, name=name),
                }
            )
        click.echo(json.dumps(payload, indent=2))
        return

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
@click.option(
    "--dry-run",
    is_flag=True,
    help="Preview the export plan without writing files.",
)
@click.option(
    "-y",
    "--yes",
    is_flag=True,
    help="Confirm writes (non-interactive; accepted for script uniformity).",
)
def skills_export(dest, package, clean, dry_run, yes):
    """Export skills to .claude/skills/ for Claude Code discovery.

    \b
    Examples:
      scitex skills export                     # Export all to .claude/skills/
      scitex skills export --package scitex-stats
      scitex skills export --dest /tmp/skills  # Custom destination
      scitex skills export --clean             # Clean export
      $ scitex skills export --dry-run
    """
    from pathlib import Path

    dest_path = Path(dest) if dest else None
    mode = "upgrade" if clean else "export"
    if dry_run:
        target = dest_path or Path(".claude/skills/")
        scope = package or "all packages"
        click.echo(
            f"dry-run: would export skills for {scope} to {target} (mode={mode})"
        )
        return

    from scitex_dev.skills import export_skills

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


def _scitex_dir():
    """User-state root: $SCITEX_DIR (default ~/.scitex)."""
    import os
    from pathlib import Path

    return Path(os.environ.get("SCITEX_DIR", Path.home() / ".scitex"))


def _bundled_skills_root():
    """Directory holding the bundled per-package skill trees (self-contained)."""
    from pathlib import Path

    import scitex

    return Path(scitex.__file__).resolve().parent / "_skills"


@skills.command("install")
@click.option("--package", default=None, help="Install only this package.")
@click.option(
    "--dest",
    type=click.Path(),
    default=None,
    help="Destination root (default: ~/.scitex/dev/skills/).",
)
@click.option(
    "--claude-symlink",
    is_flag=True,
    help="Also expose the install at ~/.claude/skills/scitex/.",
)
@click.option(
    "--dry-run",
    is_flag=True,
    help="Preview the links without creating them.",
)
@click.option(
    "-y",
    "--yes",
    is_flag=True,
    help="Replace conflicting links without asking (never prompts).",
)
def skills_install(dest, package, claude_symlink, dry_run, yes):
    """Install bundled skills as symlinks under ~/.scitex/dev/skills/.

    \b
    Examples:
      scitex skills install                        # Link all bundles
      scitex skills install --package scitex       # Link one bundle
      scitex skills install --claude-symlink       # Also expose to Claude Code
      $ scitex skills install --dry-run
    """  # noqa: D301
    from pathlib import Path

    src_root = _bundled_skills_root()
    if not src_root.is_dir():
        click.secho(f"No bundled skills found at {src_root}", fg="yellow")
        raise SystemExit(1)
    bundles = sorted(p for p in src_root.iterdir() if p.is_dir())
    if package:
        bundles = [p for p in bundles if p.name == package]
        if not bundles:
            click.secho(f"Skill not found: {package}", fg="red")
            raise SystemExit(1)

    dest_root = Path(dest).expanduser() if dest else (_scitex_dir() / "dev" / "skills")
    plans = [(src, dest_root / src.name) for src in bundles]
    conflicts = [link for _, link in plans if link.is_symlink() or link.exists()]
    if conflicts and not yes and not dry_run:
        click.secho(
            "Refusing to replace existing paths (pass --yes to replace):",
            fg="red",
            err=True,
        )
        for link in conflicts:
            click.echo(f"  {link}", err=True)
        raise SystemExit(1)

    actions = []
    for src, link in plans:
        if link.is_symlink() and link.resolve() == src.resolve():
            actions.append(("keep", src, link))
        elif (link.is_symlink() or link.exists()) and yes and not dry_run:
            actions.append(("replace", src, link))
        elif link.is_symlink() or link.exists():
            actions.append(("conflict", src, link))
        else:
            actions.append(("link", src, link))

    if dry_run:
        for verb, src, link in actions:
            click.echo(f"dry-run: would {verb} {link} -> {src}")
        if claude_symlink:
            click.echo(
                f"dry-run: would link {Path.home() / '.claude' / 'skills' / 'scitex'}"
                f" -> {dest_root}"
            )
        return

    for verb, src, link in actions:
        if verb == "keep":
            click.echo(f"  keep {link}")
        elif verb == "conflict":
            click.secho(f"  skip (exists, pass --yes to replace) {link}", fg="yellow")
        else:
            if verb == "replace" and (link.is_symlink() or link.is_file()):
                link.unlink()
            elif verb == "replace":
                import shutil

                shutil.rmtree(link)
            dest_root.mkdir(parents=True, exist_ok=True)
            link.symlink_to(src, target_is_directory=True)
            click.echo(f"  {verb} {link} -> {src}")

    if claude_symlink:
        claude_link = Path.home() / ".claude" / "skills" / "scitex"
        if claude_link.is_symlink() and claude_link.resolve() == dest_root.resolve():
            click.echo(f"  keep {claude_link}")
        else:
            if claude_link.is_symlink() or claude_link.exists():
                if not yes:
                    click.secho(
                        f"  skip (exists, pass --yes to replace) {claude_link}",
                        fg="yellow",
                    )
                else:
                    if claude_link.is_symlink() or claude_link.is_file():
                        claude_link.unlink()
                    else:
                        import shutil

                        shutil.rmtree(claude_link)
                    claude_link.parent.mkdir(parents=True, exist_ok=True)
                    claude_link.symlink_to(dest_root, target_is_directory=True)
                    click.echo(f"  link {claude_link} -> {dest_root}")
            else:
                claude_link.parent.mkdir(parents=True, exist_ok=True)
                claude_link.symlink_to(dest_root, target_is_directory=True)
                click.echo(f"  link {claude_link} -> {dest_root}")

    click.echo()
    click.secho(f"Installed {len(plans)} skill bundle(s) to {dest_root}", fg="green")
