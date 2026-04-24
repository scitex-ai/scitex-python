#!/usr/bin/env python3
"""Compute current SciTeX ecosystem stats for GitHub About / README.

Authoritative counts are taken from the live `scitex` CLI (must be importable
in the env running this script) so the numbers always match what users see:

    modules : count of `src/scitex/*/` public sub-packages (umbrella surface)
    cli     : leaf commands from `scitex --help-recursive --json`
    mcp     : `scitex mcp list-tools --json` → `total`
    skills  : sum of all entries from `scitex skills list --json`

Outputs a single About line by default:

    Python toolkit for reproducible science. {N} modules, {C} CLI commands,
    {T} MCP tools, and {S} skills. From raw data to manuscript.

Usage:
    python scripts/compute_ecosystem_stats.py [--github-about]
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

UMBRELLA_SRC = Path(__file__).resolve().parent.parent / "src" / "scitex"

ABOUT_TEMPLATE = (
    "Python toolkit for reproducible science \u2014 from raw data to manuscript. "
    "Includes {modules} modules, {cli} CLI commands, "
    "{mcp} MCP tools, and {skills} skills."
)


def count_modules() -> int:
    """Public submodules directly under src/scitex/ (exclude _private dirs)."""
    if not UMBRELLA_SRC.exists():
        return 0
    return sum(
        1
        for p in UMBRELLA_SRC.iterdir()
        if p.is_dir() and not p.name.startswith("_") and not p.name.startswith(".")
    )


def _scitex_json(args: list[str]) -> dict | list | None:
    """Invoke `scitex ... --json`, return parsed JSON or None on failure."""
    try:
        proc = subprocess.run(
            ["scitex", *args, "--json"],
            capture_output=True,
            text=True,
            timeout=60,
            check=False,
        )
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return None
    if proc.returncode != 0:
        return None
    try:
        return json.loads(proc.stdout)
    except json.JSONDecodeError:
        return None


def count_cli_commands() -> int:
    """Leaf commands in `scitex --help-recursive --json`."""
    d = _scitex_json(["--help-recursive"])
    if not d:
        return 0
    # payload is nested under data.subcommands for the recursive dump
    root = d.get("data", d) if isinstance(d, dict) else d
    if not isinstance(root, dict):
        return 0

    def walk(node):
        subs = node.get("subcommands") or {}
        if not subs:
            yield 1
            return
        for child in subs.values():
            yield from walk(child)

    return sum(walk(root))


def count_mcp_tools() -> int:
    """`scitex mcp list-tools --json` → total field."""
    d = _scitex_json(["mcp", "list-tools"])
    if isinstance(d, dict):
        if "total" in d:
            return int(d["total"])
        inner = d.get("data")
        if isinstance(inner, dict) and "total" in inner:
            return int(inner["total"])
    return 0


def count_skills() -> int:
    """`scitex skills list --json` → sum of per-package entries."""
    d = _scitex_json(["skills", "list"])
    if isinstance(d, dict):
        inner = d.get("data", d)
        if isinstance(inner, dict):
            return sum(len(v) for v in inner.values() if isinstance(v, list))
    return 0


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "--github-about",
        action="store_true",
        help="Print only the About one-liner (no labels).",
    )
    args = ap.parse_args(argv)

    modules = count_modules()
    cli = count_cli_commands()
    mcp = count_mcp_tools()
    skills = count_skills()

    about = ABOUT_TEMPLATE.format(modules=modules, cli=cli, mcp=mcp, skills=skills)

    if args.github_about:
        print(about)
    else:
        print(f"modules = {modules}")
        print(f"cli     = {cli}")
        print(f"mcp     = {mcp}")
        print(f"skills  = {skills}")
        print()
        print(about)
    return 0


if __name__ == "__main__":
    sys.exit(main())
