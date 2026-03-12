#!/usr/bin/env python3
# Timestamp: 2026-01-14
# File: src/scitex/cli/scholar/_library.py
# ----------------------------------------

"""Library and config commands for Scholar CLI."""

from __future__ import annotations

from pathlib import Path

import click

from scitex.config import get_paths

from ._utils import output_json


@click.command()
@click.option("--project", "-p", help="Show specific project")
@click.option("--json", "json_output", is_flag=True, help="Output as JSON")
def library(project, json_output):
    """
    Show your paper library

    \b
    Examples:
        scitex scholar library
        scitex scholar library --json
        scitex scholar library --project neuroscience
    """
    library_path = get_paths().scholar_library

    if not library_path.exists():
        result = {
            "success": True,
            "empty": True,
            "message": "Library is empty",
            "path": str(library_path),
        }
        if json_output:
            output_json(result)
        else:
            click.echo(
                "Library is empty. Fetch papers with: scitex scholar fetch <doi>"
            )
        return

    if project:
        _show_project(library_path, project, json_output)
    else:
        _show_library_summary(library_path, json_output)


def _show_project(library_path: Path, project: str, json_output: bool):
    """Show a specific project."""
    from scitex_dev import ErrorCode

    project_path = library_path / project
    if not project_path.exists():
        result = {
            "success": False,
            "error": f"Project '{project}' not found",
            "error_code": ErrorCode.FILE_NOT_FOUND.value,
        }
        if json_output:
            output_json(result)
        else:
            click.echo(f"Project '{project}' not found")
        return

    papers = [item.name for item in sorted(project_path.iterdir()) if item.is_symlink()]
    result = {
        "success": True,
        "project": project,
        "path": str(project_path),
        "paper_count": len(papers),
        "papers": papers,
    }

    if json_output:
        output_json(result)
    else:
        click.echo(f"\nProject: {project}")
        click.echo(f"Location: {project_path}")
        click.echo("\nPapers:")
        for paper in papers:
            click.echo(f"  {paper}")


def _show_library_summary(library_path: Path, json_output: bool):
    """Show library summary."""
    master_path = library_path / "MASTER"
    project_dirs = [
        d for d in library_path.iterdir() if d.is_dir() and d.name != "MASTER"
    ]

    total_papers = len(list(master_path.iterdir())) if master_path.exists() else 0
    projects = []
    for proj_dir in sorted(project_dirs):
        paper_count = len([p for p in proj_dir.iterdir() if p.is_symlink()])
        projects.append({"name": proj_dir.name, "paper_count": paper_count})

    result = {
        "success": True,
        "path": str(library_path),
        "total_papers": total_papers,
        "project_count": len(projects),
        "projects": projects,
    }

    if json_output:
        output_json(result)
    else:
        click.echo(f"\nTotal papers: {total_papers}")
        if projects:
            click.echo(f"\nProjects ({len(projects)}):")
            for proj in projects:
                click.echo(f"  {proj['name']} ({proj['paper_count']} papers)")
        else:
            click.echo("\nNo projects. Use --project/-p when adding papers.")


@click.command()
@click.option("--json", "json_output", is_flag=True, help="Output as JSON")
def config(json_output):
    """Show Scholar configuration."""
    library_path = get_paths().scholar_library
    chrome_config_path = Path.home() / ".config" / "google-chrome"

    total_papers = 0
    if library_path.exists():
        master_path = library_path / "MASTER"
        if master_path.exists():
            total_papers = len(list(master_path.iterdir()))

    result = {
        "success": True,
        "library_path": str(library_path),
        "library_exists": library_path.exists(),
        "total_papers": total_papers,
        "chrome_available": chrome_config_path.exists(),
        "chrome_path": str(chrome_config_path),
    }

    if json_output:
        output_json(result)
    else:
        click.echo("\n=== SciTeX Scholar ===\n")
        click.echo(f"Library: {library_path}")
        if library_path.exists():
            click.echo(f"Papers:  {total_papers}")
        click.echo(
            f"\nChrome:  {'Available' if chrome_config_path.exists() else 'Not found'}"
        )


# EOF
