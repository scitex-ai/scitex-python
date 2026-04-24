#!/usr/bin/env python3
"""Compute current SciTeX ecosystem stats for GitHub About / README.

Outputs a single line ready for `gh api PATCH description`:

    Python toolkit for reproducible science. {N} modules, {C} CLI commands,
    {T} MCP tools, and {S} skills. From raw data to manuscript.

Counts are derived from the current scitex-python checkout plus (optionally)
the sibling scitex-* repos under --projects-root.

Usage:
    python scripts/compute_ecosystem_stats.py \
        [--projects-root /home/ywatanabe/proj] \
        [--github-about]   # print the About one-liner only
"""

from __future__ import annotations

import argparse
import os
import re
import sys
from pathlib import Path

UMBRELLA_SRC = Path(__file__).resolve().parent.parent / "src" / "scitex"

DEFAULT_ABOUT_TEMPLATE = (
    "Python toolkit for reproducible science. "
    "{modules} modules, {cli} CLI commands, {mcp} MCP tools, and {skills} skills. "
    "From raw data to manuscript."
)


def count_modules() -> int:
    """Public submodules directly under src/scitex/ (exclude _private dirs)."""
    return sum(
        1
        for p in UMBRELLA_SRC.iterdir()
        if p.is_dir() and not p.name.startswith("_") and not p.name.startswith(".")
    )


def count_cli_commands(projects_root: Path) -> int:
    """Sum of `[project.scripts]` entries across installed scitex-* repos."""
    total = 0
    for pyproject in sorted(projects_root.glob("scitex-*/pyproject.toml")):
        try:
            text = pyproject.read_text()
        except OSError:
            continue
        # Naive but robust: count non-blank, non-comment lines inside
        # [project.scripts] up to the next [section].
        m = re.search(r"\[project\.scripts\][^\[]*", text, re.S)
        if not m:
            continue
        block = m.group(0).splitlines()[1:]
        for line in block:
            s = line.strip()
            if s and not s.startswith("#") and "=" in s:
                total += 1
    # also the umbrella itself
    umbrella_py = UMBRELLA_SRC.parent.parent / "pyproject.toml"
    if umbrella_py.exists():
        text = umbrella_py.read_text()
        m = re.search(r"\[project\.scripts\][^\[]*", text, re.S)
        if m:
            for line in m.group(0).splitlines()[1:]:
                s = line.strip()
                if s and not s.startswith("#") and "=" in s:
                    total += 1
    return total


def count_mcp_tools(projects_root: Path) -> int:
    """Count @mcp.tool() decorators across all scitex-*/src trees."""
    total = 0
    patterns = (r"@mcp\.tool\b", r"@app\.tool\b", r"@mcp_server\.tool\b")
    rx = re.compile("|".join(patterns))
    for src_py in projects_root.glob("scitex-*/src/**/*.py"):
        try:
            total += len(rx.findall(src_py.read_text(errors="ignore")))
        except OSError:
            continue
    return total


def count_skills(projects_root: Path) -> int:
    """Count non-index leaf .md files across all scitex-*/_skills/ trees."""
    total = 0
    seen: set[str] = set()
    # Per-package in-repo _skills/
    for skill_md in projects_root.glob("scitex-*/src/*/_skills/*/*.md"):
        if skill_md.name in {"SKILL.md", "MANIFEST.md", "README.md"}:
            continue
        key = str(skill_md.relative_to(projects_root))
        if key in seen:
            continue
        seen.add(key)
        total += 1
    # Umbrella's own general/ skills
    for skill_md in UMBRELLA_SRC.glob("_skills/general/*.md"):
        if skill_md.name in {"SKILL.md", "MANIFEST.md", "README.md"}:
            continue
        total += 1
    return total


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "--projects-root",
        type=Path,
        default=Path(os.environ.get("HOME", "/")) / "proj",
    )
    ap.add_argument(
        "--github-about",
        action="store_true",
        help="Print only the About one-liner (no labels).",
    )
    args = ap.parse_args(argv)

    modules = count_modules()
    cli = count_cli_commands(args.projects_root)
    mcp = count_mcp_tools(args.projects_root)
    skills = count_skills(args.projects_root)

    about = DEFAULT_ABOUT_TEMPLATE.format(
        modules=modules, cli=cli, mcp=mcp, skills=skills
    )

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
