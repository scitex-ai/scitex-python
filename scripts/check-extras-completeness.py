#!/usr/bin/env python3
"""Verify every public module has an extras group, and 'all' includes them.

Exit codes:
    0 - All checks pass.
    1 - Missing extras groups or incomplete 'all' aggregation.
"""

from __future__ import annotations

import sys
from pathlib import Path

import tomllib

# Directories that are NOT public modules (skip these)
SKIP_DIRS = {
    "__pycache__",
    "_dev",
    "_mcp",
    "skills",
}

# Module dirs whose extras key uses a different name
DIR_TO_EXTRAS = {
    "dev": "devtools",  # 'dev' extras is for testing tools
}

# Extras that should NOT be in 'all'
EXCLUDE_FROM_ALL = {"dev", "all"}


def main() -> int:
    root = Path(__file__).resolve().parent.parent
    pyproject_path = root / "pyproject.toml"
    modules_dir = root / "src" / "scitex"

    with open(pyproject_path, "rb") as f:
        data = tomllib.load(f)

    extras = set(data["project"]["optional-dependencies"].keys())
    all_refs = {
        ref.replace("scitex[", "").replace("]", "")
        for ref in data["project"]["optional-dependencies"].get("all", [])
    }

    # Discover public module directories
    module_dirs = sorted(
        d.name
        for d in modules_dir.iterdir()
        if d.is_dir()
        and d.name not in SKIP_DIRS
        and not d.name.startswith("_")
        and not d.name.startswith(".")
    )

    errors = []

    # Check 1: Every public module dir has a matching extras key
    for mod in module_dirs:
        extras_key = DIR_TO_EXTRAS.get(mod, mod)
        if extras_key not in extras:
            errors.append(
                f"Module '{mod}' has no extras group '{extras_key}' in pyproject.toml"
            )

    # Check 2: 'all' includes every individual extras key (except exclusions)
    expected_in_all = extras - EXCLUDE_FROM_ALL
    missing_from_all = expected_in_all - all_refs
    if missing_from_all:
        for key in sorted(missing_from_all):
            errors.append(f"Extras group '{key}' is missing from 'all' aggregation")

    # Report
    if errors:
        print(f"FAIL: {len(errors)} error(s) found:\n")
        for err in errors:
            print(f"  - {err}")
        return 1

    print(
        f"PASS: {len(module_dirs)} modules, {len(extras)} extras groups, "
        f"{len(all_refs)} entries in 'all'"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
