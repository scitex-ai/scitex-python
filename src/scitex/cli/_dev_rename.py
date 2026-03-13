#!/usr/bin/env python3
# Timestamp: 2026-02-14
# File: scitex/cli/_dev_rename.py

"""CLI command for bulk rename operations."""

import click


@click.command("rename")
@click.argument("pattern")
@click.argument("replacement")
@click.argument("directory", default=".")
@click.option(
    "-n",
    "--no-dry-run",
    is_flag=True,
    help="Actually perform replacements (default is dry run)",
)
@click.option("--no-django-safe", is_flag=True, help="Disable Django-safe mode")
@click.option("-e", "--exclude", multiple=True, help="Additional exclude patterns")
@click.option("-b", "--backup", is_flag=True, help="Create backup before changes")
@click.option("--json", "as_json", is_flag=True, help="Output as JSON")
@click.option("-f", "--force", is_flag=True, help="Skip uncommitted changes check")
def rename(
    pattern,
    replacement,
    directory,
    no_dry_run,
    no_django_safe,
    exclude,
    backup,
    as_json,
    force,
):
    """
    Bulk rename files, contents, directories, and symlinks.

    \b
    Two-level filtering: PATH-level (which files) and SRC-level (which content).
    Django-safe by default (protects db_table, related_name, migrations).

    \b
    Execution order:
      1. File contents (safe - doesn't change paths)
      2. Symlink targets and names
      3. File names
      4. Directory names (deepest first)

    \b
    Examples:
      scitex dev rename 'old_name' 'new_name'              # Dry run
      scitex dev rename -n 'old_name' 'new_name'            # Live mode
      scitex dev rename 'old' 'new' ./src                   # Specific directory
      scitex dev rename -e '*.log' 'old' 'new'              # Extra exclude
      scitex dev rename --no-django-safe 'old' 'new'        # No Django protection
    """
    import json as json_module

    from scitex._dev._rename import RenameConfig, bulk_rename

    config = RenameConfig(
        pattern=pattern,
        replacement=replacement,
        directory=directory,
        dry_run=not no_dry_run,
        django_safe=not no_django_safe,
        create_backup=backup,
        extra_excludes=list(exclude),
    )

    if not config.dry_run and not force:
        from scitex._dev._rename._safety import has_uncommitted_changes

        if has_uncommitted_changes(directory):
            click.secho(
                "ERROR: Uncommitted changes detected. Commit or stash first.",
                fg="red",
            )
            raise SystemExit(1)

    result = bulk_rename(config)

    if as_json:
        from dataclasses import asdict

        click.echo(json_module.dumps(asdict(result), indent=2))
        return

    _print_rename_result(result, pattern, replacement)


def _print_rename_result(result, pattern, replacement):
    """Print human-readable rename results."""
    mode = "DRY RUN" if result.dry_run else "LIVE"
    click.secho(
        f"Rename [{mode}]: '{pattern}' -> '{replacement}'",
        fg="cyan",
        bold=True,
    )
    click.echo(f"  Directory: {result.directory}")
    click.echo()

    if result.contents:
        click.secho("File Contents:", fg="yellow", bold=True)
        for c in result.contents:
            prot = f" ({c['protected']} protected)" if c.get("protected") else ""
            click.echo(f"  {c['file']}: {c['matches']} matches{prot}")
        click.echo()

    if result.symlink_targets:
        click.secho("Symlink Targets:", fg="yellow", bold=True)
        for s in result.symlink_targets:
            click.echo(f"  {s['link']}: {s['old_target']} -> {s['new_target']}")
        click.echo()

    if result.symlink_names:
        click.secho("Symlink Names:", fg="yellow", bold=True)
        for s in result.symlink_names:
            click.echo(f"  {s['old_name']} -> {s['new_name']}")
        click.echo()

    if result.file_names:
        click.secho("File Names:", fg="yellow", bold=True)
        for f in result.file_names:
            click.echo(f"  {f['old_path']} -> {f['new_path']}")
        click.echo()

    if result.dir_names:
        click.secho("Directory Names:", fg="yellow", bold=True)
        for d in result.dir_names:
            click.echo(f"  {d['old_path']} -> {d['new_path']}")
        click.echo()

    if result.collisions:
        click.secho("COLLISIONS (target already exists):", fg="red", bold=True)
        for col in result.collisions:
            click.echo(f"  [{col['type']}] {col['path']}")
        click.echo()

    # Summary
    s = result.summary
    click.secho("Summary:", fg="cyan", bold=True)
    click.echo(
        f"  Content files:  {s.get('content_files', 0)}"
        f" ({s.get('content_matches', 0)} matches,"
        f" {s.get('content_protected', 0)} protected)"
    )
    click.echo(
        f"  Symlinks:       {s.get('symlink_targets_updated', 0)} targets,"
        f" {s.get('symlinks_renamed', 0)} names"
    )
    click.echo(f"  Files renamed:  {s.get('files_renamed', 0)}")
    click.echo(f"  Dirs renamed:   {s.get('dirs_renamed', 0)}")
    click.echo(f"  Collisions:     {s.get('collisions', 0)}")

    if result.collisions and result.dry_run:
        click.echo()
        click.secho(
            "WARNING: Collisions detected. Resolve before applying.",
            fg="red",
        )
    elif result.dry_run:
        click.echo()
        click.secho("No changes made (dry run). Use -n to apply.", fg="yellow")


# EOF
