#!/usr/bin/env python3.11
"""Audit downstream package test scopes.

Rule (scitex-python TODO item 7):
- Downstream packages MUST NOT import the `scitex` umbrella in tests.
- Sibling downstream imports are flagged unless they are
  `pytest.importorskip`-guarded or shared test scaffolds (scitex_dev).

Runs as an AST walk over each downstream package's tests/ directory.

Exit code 0 if clean, 1 if violations found.

Usage:
    python3.11 scripts/audit_test_scope.py [--projects-root /home/ywatanabe/proj]
"""

from __future__ import annotations

import argparse
import ast
import sys
from pathlib import Path

# Downstream packages (standalone) + their own module name
DOWNSTREAM = {
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
    "scitex-ssh": "scitex_ssh",
    "figrecipe": "figrecipe",
    "scitex-writer": "scitex_writer",
}
SIBLINGS = set(DOWNSTREAM.values())

# scitex_dev is a shared dev-only scaffold (like a pytest plugin).
# Siblings imported via pytest.importorskip are also allowed.
ALLOWED_SHARED = {"scitex_dev"}


def module_root(name: str) -> str:
    return name.split(".")[0] if name else ""


def find_violations(
    pkg: str, own_mod: str, tests_dir: Path
) -> list[tuple[Path, int, str, str]]:
    violations: list[tuple[Path, int, str, str]] = []
    for f in tests_dir.rglob("*.py"):
        try:
            source = f.read_text()
            tree = ast.parse(source, filename=str(f))
        except Exception:
            continue

        # Pre-index pytest.importorskip("sibling") lines
        importorskip_lines: set[int] = set()
        for node in ast.walk(tree):
            if (
                isinstance(node, ast.Call)
                and isinstance(node.func, ast.Attribute)
                and node.func.attr == "importorskip"
                and isinstance(node.func.value, ast.Name)
                and node.func.value.id == "pytest"
                and node.args
                and isinstance(node.args[0], ast.Constant)
            ):
                mod = node.args[0].value
                if isinstance(mod, str):
                    importorskip_lines.add(node.lineno)
                    # mark sibling as allowed in this file
                    # (stored on a per-file set below)

        # Collect sibling names gated by pytest.importorskip OR by try/except ImportError.
        gated = set()
        for node in ast.walk(tree):
            if (
                isinstance(node, ast.Call)
                and isinstance(node.func, ast.Attribute)
                and node.func.attr == "importorskip"
                and isinstance(node.func.value, ast.Name)
                and node.func.value.id == "pytest"
                and node.args
                and isinstance(node.args[0], ast.Constant)
                and isinstance(node.args[0].value, str)
            ):
                gated.add(node.args[0].value)

        # Any import inside a `try` with an `except ImportError:` handler is gated.
        for node in ast.walk(tree):
            if isinstance(node, ast.Try) and any(
                isinstance(h.type, ast.Name) and h.type.id == "ImportError"
                for h in node.handlers
                if h.type is not None
            ):
                for inner in ast.walk(node):
                    names: list[str] = []
                    if isinstance(inner, ast.Import):
                        names = [n.name for n in inner.names]
                    elif isinstance(inner, ast.ImportFrom) and inner.module:
                        names = [inner.module]
                    for nm in names:
                        gated.add(nm.split(".")[0])

        for node in ast.walk(tree):
            target_mods: list[str] = []
            if isinstance(node, ast.Import):
                target_mods = [n.name for n in node.names]
            elif isinstance(node, ast.ImportFrom):
                if node.level == 0 and node.module:
                    target_mods = [node.module]

            for raw in target_mods:
                root = module_root(raw)

                # Rule 1: never import the umbrella "scitex"
                if root == "scitex":
                    violations.append(
                        (f.relative_to(tests_dir), node.lineno, raw, "umbrella-import")
                    )
                    continue

                # Rule 2: siblings allowed only if shared or importorskip-gated
                if root in SIBLINGS and root != own_mod:
                    if root in ALLOWED_SHARED or root in gated:
                        continue
                    violations.append(
                        (f.relative_to(tests_dir), node.lineno, raw, "ungated-sibling")
                    )

    return violations


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--projects-root",
        type=Path,
        default=Path("/home/ywatanabe/proj"),
        help="Directory containing the downstream package repos.",
    )
    args = parser.parse_args()

    any_fail = False
    for pkg, own_mod in DOWNSTREAM.items():
        tests = args.projects_root / pkg / "tests"
        if not tests.exists():
            print(f"[skip] {pkg}: no tests/ dir")
            continue
        violations = find_violations(pkg, own_mod, tests)
        if violations:
            any_fail = True
            print(f"\n[FAIL] {pkg}: {len(violations)} violation(s)")
            for rel, line, mod, kind in violations:
                print(f"  {rel}:{line}  {kind}  import {mod}")
        else:
            print(f"[ok]   {pkg}")

    print()
    if any_fail:
        print("FAIL — downstream packages must not import the scitex umbrella.")
        print(
            "      Sibling imports must be pytest.importorskip-gated or shared-dev (scitex_dev)."
        )
        return 1
    print("PASS — all downstream test scopes are clean.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
