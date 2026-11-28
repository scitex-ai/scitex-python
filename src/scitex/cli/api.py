#!/usr/bin/env python3
"""``scitex api list`` — the API surface of every installed SciTeX package.

The global, offline listing: for each installed ecosystem package (the
scitex-dev registry), its declared REST operations (``scitex.apis``), its
MCP tools and the API normalization findings — composed by scitex-sdk's
``aggregate()``, the same function each package's own ``<pkg> api list``,
the hub inventory and the CI audit use. There is no separate registry.
"""

from __future__ import annotations

import importlib.util
from pathlib import Path

import click

SDK_FLOOR = "0.3.27"


def _sdk():
    try:
        from scitex_sdk.app import api_inventory
    except ImportError as exc:
        raise click.ClickException(
            f"`scitex api` needs scitex-sdk>={SDK_FLOOR}: "
            f"pip install 'scitex-sdk>={SDK_FLOOR}' ({exc})"
        ) from exc
    return api_inventory


def installed_specs(api_inventory, packages: tuple[str, ...] = ()) -> list:
    """One ``PackageSpec`` per installed registry peer (or the named ones)."""
    try:
        from scitex_dev._ecosystem._core import ECOSYSTEM
    except ImportError:
        ECOSYSTEM = {}
    specs = []
    for pip_name, info in sorted(ECOSYSTEM.items()):
        if packages and pip_name not in packages:
            continue
        if info.get("archived") or info.get("category") in ("umbrella", "template"):
            continue
        import_name = info.get("import_name") or pip_name.replace("-", "_")
        try:
            if importlib.util.find_spec(import_name) is None:
                continue
        except (ImportError, ValueError):
            continue
        namespace = info.get("umbrella_subcommand", pip_name.removeprefix("scitex-"))
        specs.append(
            api_inventory.PackageSpec(
                pip_name, import_name=import_name, namespace=namespace.replace("-", "_")
            )
        )
    found = {spec.distribution for spec in specs}
    specs += [api_inventory.PackageSpec(p) for p in packages if p not in found]
    if not specs and not packages:
        specs = api_inventory.discover_specs()
    return specs


@click.group("api", invoke_without_command=True)
@click.pass_context
def api(ctx: click.Context) -> None:
    """API surface of installed SciTeX packages (REST operations + MCP tools).

    \b
    Example:
      $ scitex api list
      $ scitex api list --package scitex-dataset --format json
    """
    if ctx.invoked_subcommand is None:
        click.echo(ctx.get_help())


@api.command("list")
@click.option(
    "--package",
    "packages",
    multiple=True,
    help="Limit to these distributions (repeatable). Default: every installed peer.",
)
@click.option(
    "--format",
    "fmt",
    type=click.Choice(["csv", "json", "md"]),
    default="md",
    show_default=True,
)
@click.option(
    "--output", "-o", type=click.Path(dir_okay=False), help="Write to a file."
)
@click.option("--strict", is_flag=True, help="Exit 1 when any entry violates a rule.")
@click.option("--json", "as_json", is_flag=True, help="Same as --format json.")
def list_(
    packages: tuple[str, ...], fmt: str, output: str | None, strict: bool, as_json: bool
) -> None:
    """List REST operations and MCP tools of installed packages, with rule findings.

    \b
    Example:
      $ scitex api list
      $ scitex api list --format csv -o api.csv
      $ scitex api list --package scitex-dataset --strict
    """
    inv = _sdk()
    doc = inv.aggregate(installed_specs(inv, packages))
    text = inv.RENDERERS["json" if as_json else fmt](doc)
    if output:
        Path(output).write_text(text, encoding="utf-8")
        click.echo(f"wrote {output}", err=True)
    else:
        click.echo(text, nl=False)
    totals = doc["totals"]
    if strict and totals["programmatic"] != totals["conformant"]:
        raise click.ClickException(
            f"{totals['programmatic'] - totals['conformant']} entries violate API rules"
        )


__all__ = ["api", "installed_specs"]
