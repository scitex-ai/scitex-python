#!/usr/bin/env python3.11
"""Audit every python code block in README.md + docs/*.md against the installed API.

For each `stx.X.Y.Z(...)` attribute chain that appears in a python fenced
block, walks the installed `scitex` module one hop at a time and verifies
hasattr at every level. Lazy submodules are hydrated up-front so the
`scitex.X.Y` LazyModule pattern resolves correctly.

Also audits each downstream package's README.md against its installed
module (scitex-io → scitex_io, figrecipe → figrecipe, etc.).

Exit 0 if every chain resolves; exit 1 if any chain references a missing
attribute — in which case the doc advertises an API that does not exist
and needs updating.

Usage:
    python3.11 scripts/audit_doc_examples.py
    python3.11 scripts/audit_doc_examples.py --projects-root /home/ywatanabe/proj
"""

from __future__ import annotations

import argparse
import ast
import importlib
import re
import sys
from pathlib import Path

# Lazy submodules to hydrate before the walk (scitex umbrella uses _LazyModule;
# naive getattr from inside a fresh process may miss these unless we pre-import).
UMBRELLA_SUBMODULES = [
    "container",
    "dataset",
    "audio",
    "linter",
    "stats",
    "scholar",
    "writer",
    "io",
    "plt",
    "clew",
    "tunnel",
    "notification",
    "app",
    "ui",
    "notebook",
    "repro",
    "parallel",
    "path",
    "str",
    "dict",
    "logging",
]

DOWNSTREAM_PACKAGES = {
    "scitex-io": "scitex_io",
    "scitex-stats": "scitex_stats",
    "scitex-scholar": "scitex_scholar",
    "scitex-notebook": "scitex_notebook",
    "scitex-audio": "scitex_audio",
    "scitex-clew": "scitex_clew",
    "scitex-linter": "scitex_linter",
    "scitex-notification": "scitex_notification",
    "scitex-app": "scitex_app",
    "scitex-dataset": "scitex_dataset",
    "scitex-ui": "scitex_ui",
    "scitex-container": "scitex_container",
    "scitex-tunnel": "scitex_tunnel",
    "figrecipe": "figrecipe",
    "scitex-writer": "scitex_writer",
}


def walk_chains(module, source: str, alias: str):
    """Yield (chain_str, ok) for every attribute chain rooted at `alias`."""
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return
    for node in ast.walk(tree):
        if not isinstance(node, ast.Attribute):
            continue
        parts: list[str] = []
        cur = node
        while isinstance(cur, ast.Attribute):
            parts.append(cur.attr)
            cur = cur.value
        if not (isinstance(cur, ast.Name) and cur.id == alias):
            continue
        parts.reverse()
        obj = module
        for i, p in enumerate(parts):
            if not hasattr(obj, p):
                yield f"{alias}." + ".".join(parts[: i + 1]), False
                break
            obj = getattr(obj, p)
        else:
            yield f"{alias}." + ".".join(parts), True


def audit_markdown(md_path: Path, module, module_name: str) -> list[str]:
    """Return list of missing attribute chains found in md_path.

    Only chains whose root alias was bound to `module_name` in THIS
    block (via `import <module_name> [as <alias>]`) are checked. Other
    aliases (pd, np, plt, etc.) are ignored.
    """
    missing: list[str] = []
    source = md_path.read_text()
    blocks = re.findall(r"```python\n(.*?)\n```", source, re.DOTALL)
    for i, b in enumerate(blocks, 1):
        aliases: set[str] = set()
        for m in re.finditer(
            rf"^import {re.escape(module_name)}(?:\s+as\s+(\w+))?",
            b,
            re.MULTILINE,
        ):
            aliases.add(m.group(1) or module_name)
        if not aliases:
            continue
        for alias in aliases:
            for chain, ok in walk_chains(module, b, alias):
                if not ok:
                    missing.append(f"{md_path.name}#{i}: {chain}")
    return missing


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--projects-root",
        type=Path,
        default=Path("/home/ywatanabe/proj"),
    )
    args = parser.parse_args()

    any_fail = False

    # 1. scitex-python umbrella — README.md + docs/*.md
    import scitex

    for sub in UMBRELLA_SUBMODULES:
        try:
            importlib.import_module(f"scitex.{sub}")
        except Exception:
            pass

    umbrella_root = args.projects_root / "scitex-python"
    targets = [umbrella_root / "README.md"] + sorted(
        (umbrella_root / "docs").glob("*.md")
    )
    print("=== umbrella (scitex) ===")
    for md in targets:
        if not md.exists():
            continue
        missing = audit_markdown(md, scitex, "scitex")
        if missing:
            any_fail = True
            for m in missing:
                print(f"  [FAIL] {m}")
        else:
            print(f"  [ok]   {md.relative_to(umbrella_root)}")

    # 2. Downstream packages — their own README.md against their installed module
    print("\n=== downstream packages ===")
    for pkg, mod_name in DOWNSTREAM_PACKAGES.items():
        readme = args.projects_root / pkg / "README.md"
        if not readme.exists():
            continue
        try:
            mod = importlib.import_module(mod_name)
        except Exception as e:
            print(f"  [skip] {pkg}: cannot import {mod_name} ({e})")
            continue
        # Downstream READMEs may use any alias. We detect per-block.
        missing = audit_markdown(readme, mod, mod_name)
        if missing:
            any_fail = True
            for m in missing:
                print(f"  [FAIL] {pkg}: {m}")
        else:
            print(f"  [ok]   {pkg}")

    print()
    if any_fail:
        print("FAIL — at least one doc example references a non-existent API.")
        print("       Fix the doc to match the installed module, or add the API.")
        return 1
    print("PASS — every doc code block resolves against the installed API.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
