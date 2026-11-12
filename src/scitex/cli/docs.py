#!/usr/bin/env python3
"""SciTeX Docs CLI — Browse and search documentation across the ecosystem."""

import sys

import click


@click.group(invoke_without_command=True)
@click.option("--list", "list_pages", is_flag=True, help="List doc pages")
@click.option("--page", default=None, help="Specific page")
@click.option(
    "--json",
    "as_json",
    is_flag=True,
    help="Output as structured JSON (Result envelope).",
)
@click.option("--tldr", is_flag=True, help="Quick-start summary (< 20 lines)")
@click.option("--format", "fmt", type=click.Choice(["html", "json"]), default=None)
@click.option("--help-recursive", is_flag=True, help="Show help for all subcommands")
@click.pass_context
def docs(ctx, list_pages, page, as_json, tldr, fmt, help_recursive):
    """Browse and search documentation across the SciTeX ecosystem.

    \b
    Commands:
      scitex docs                    # Show help
      scitex docs --tldr             # Quick examples (< 20 lines)
      scitex docs --list             # List all doc pages
      scitex docs --page api         # Specific page
      scitex docs --json             # Structured JSON for agents
      scitex docs search "save fig"  # Search across all packages
      scitex docs build              # Build Sphinx docs

    \b
    Examples:
      scitex docs --tldr
      scitex docs --page api --format json
      scitex docs search "statistics test"
    """
    if ctx.invoked_subcommand is not None:
        return

    # Handle --help-recursive
    if help_recursive:
        if as_json:
            from . import help_recursive_to_json

            help_recursive_to_json(ctx, docs)
        else:
            from . import print_help_recursive

            print_help_recursive(ctx, docs)
        ctx.exit(0)
        return

    # Handle --json at group level (list subcommands)
    if as_json and not list_pages and not page and not tldr:
        if not list_pages and not page and not tldr and not fmt:
            from . import group_to_json

            group_to_json(ctx, docs)
            return

    if tldr:
        _show_tldr(as_json)
        return

    if list_pages:
        _show_list(as_json)
        return

    if page:
        _show_page(page, fmt, as_json)
        return

    # Default: show help (consistent with other groups)
    click.echo(ctx.get_help())


def _show_tldr(as_json):
    """Show quick-start examples."""
    tldr_text = """\
# SciTeX Quick Start

import scitex as stx

# Session — reproducible experiment tracking
@stx.session
def main(param1="default", CONFIG=stx.INJECTED, plt=stx.INJECTED):
    stx.io.save(results, "results.csv")
    return 0

# I/O — universal save/load (30+ formats)
stx.io.save(df, "data.csv")
data = stx.io.load("data.csv")

# Stats — publication-ready statistics
result = stx.stats.test_ttest_ind(g1, g2, return_as="dataframe")

# Plotting — auto CSV export
fig, ax = stx.plt.subplots()
ax.plot_line(x, y)
stx.io.save(fig, "plot.png")  # saves plot.png + plot.csv

# Scholar — literature management
# scitex scholar fetch "10.1038/nature12373"
# scitex scholar search "neural networks" --limit 20
"""
    if as_json:
        from scitex_dev import Result

        click.echo(Result(success=True, data={"tldr": tldr_text}).to_json())
    else:
        click.echo(tldr_text)


def _show_list(as_json):
    """List all doc pages across packages."""
    from scitex_dev import get_docs

    overview = get_docs()
    pages = []
    if isinstance(overview, dict):
        for pkg_name, info in sorted(overview.items()):
            if isinstance(info, dict):
                for p in info.get("pages", []):
                    name = p.get("name", p) if isinstance(p, dict) else p
                    pages.append({"package": pkg_name, "page": name})

    if as_json:
        from scitex_dev import Result

        click.echo(Result(success=True, data={"pages": pages}).to_json())
    else:
        for entry in pages:
            click.echo(f"  {entry['package']}/{entry['page']}")


def _show_page(page, fmt, as_json):
    """Show a specific doc page."""
    from scitex_dev import get_docs

    # Try to find the page in any package
    overview = get_docs()
    if isinstance(overview, dict):
        for pkg_name in overview:
            try:
                result = get_docs(package=pkg_name, format=fmt, page=page)
                if result is not None:
                    if as_json:
                        from scitex_dev import Result

                        click.echo(
                            Result(
                                success=True,
                                data={
                                    "package": pkg_name,
                                    "page": page,
                                    "content": str(result),
                                },
                            ).to_json()
                        )
                    else:
                        click.echo(str(result))
                    return
            except (LookupError, Exception):
                continue

    click.secho(f"Page '{page}' not found", fg="red", err=True)
    sys.exit(1)


@docs.command("search")
@click.argument("query")
@click.option("--package", "-p", help="Search within a specific package")
@click.option("--max-results", "-n", type=int, default=10, help="Max results")
@click.option("--json", "as_json", is_flag=True, help="Output as JSON")
def docs_search(query, package, max_results, as_json):
    """Search documentation across all SciTeX packages.

    \b
    Examples:
      scitex docs search "save figure"
      scitex docs search "statistics" --package scitex-stats
      scitex docs search "neural" --json
    """
    try:
        from scitex_dev import search_docs

        results = search_docs(query=query, package=package, max_results=max_results)

        if as_json:
            from scitex_dev import Result

            click.echo(Result(success=True, data={"results": results}).to_json())
        else:
            if not results:
                click.echo(f"No results for: {query}")
                return
            for r in results:
                click.secho(f"  {r['package']}/{r['name']}", fg="green", bold=True)
                if r.get("title"):
                    click.echo(f"    {r['title']}")
    except Exception as e:
        click.secho(f"Error: {e}", fg="red", err=True)
        sys.exit(1)


@docs.command("build")
@click.option("--package", "-p", help="Build docs for specific package")
@click.option(
    "--format",
    "fmt",
    type=click.Choice(["html", "json"]),
    default="html",
    help="Build format",
)
@click.option("--json", "as_json", is_flag=True, help="Output as JSON")
@click.option(
    "--dry-run", is_flag=True, help="Show what would be built without building"
)
@click.option(
    "--yes",
    "-y",
    is_flag=True,
    help="Accept explicit documentation building for automation (already non-interactive).",
)
def docs_build(package, fmt, as_json, dry_run, yes):
    """Build Sphinx documentation for SciTeX packages.

    \b
    Examples:
      scitex docs build
      scitex docs build --package scitex-writer
      scitex docs build --dry-run
    """
    del yes  # Explicit build is already non-interactive.
    if dry_run:
        from scitex_dev import get_docs

        overview = get_docs()
        packages = list(overview.keys()) if isinstance(overview, dict) else []
        if package:
            packages = [package]
        plan = {
            "action": "dry_run",
            "packages": packages,
            "format": fmt,
        }
        if as_json:
            from scitex_dev import Result

            click.echo(Result(success=True, data=plan).to_json())
        else:
            click.echo(f"[dry-run] Would build {fmt} docs for: {', '.join(packages)}")
        return

    from scitex_dev import Result

    try:
        from scitex_dev import build_docs

        results = build_docs(package=package, formats=[fmt])
    except Exception as exc:
        if as_json:
            click.echo(Result(success=False, error=str(exc)).to_json())
        else:
            click.secho(f"Error: {exc}", fg="red", err=True)
        sys.exit(1)

    failures = {
        name: errors
        for name, result in results.items()
        if (errors := _build_errors(result))
    }
    if as_json:
        click.echo(
            Result(
                success=not failures,
                data=results,
                error=(
                    "Documentation build failed: " + ", ".join(failures)
                    if failures
                    else None
                ),
            ).to_json()
        )
    else:
        for name in results:
            if name in failures:
                click.secho(f"  {name}: {'; '.join(failures[name])}", fg="red")
            else:
                click.secho(f"  {name}: built", fg="green")
    if failures:
        sys.exit(1)


def _build_errors(result):
    """Read package-level and per-builder errors from Dev's build result."""
    if not isinstance(result, dict):
        return []
    errors = []
    for key, value in result.items():
        if key == "error":
            errors.append(str(value))
        else:
            errors.extend(_build_errors(value))
    return errors


# EOF
