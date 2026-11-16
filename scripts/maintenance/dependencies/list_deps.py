#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2026-01-08 01:55:07 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex-code/scripts/maintenance/dependencies/list_deps.py


"""Analyze scitex module dependencies."""

# Imports
import ast
from collections import defaultdict

import scitex as stx


# Functions and Classes
def find_scitex_imports(file_path):
    """Extract scitex.* imports from a Python file."""
    try:
        with open(file_path) as f:
            tree = ast.parse(f.read())
    except Exception:
        return []

    imports = []
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom):
            if node.module and node.module.startswith("scitex."):
                parts = node.module.split(".")
                if len(parts) >= 2:
                    imports.append(parts[1])
        elif isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name.startswith("scitex."):
                    parts = alias.name.split(".")
                    if len(parts) >= 2:
                        imports.append(parts[1])

    return imports


def analyze_module_dependencies(scitex_path):
    """Analyze dependencies for each scitex submodule."""
    # scitex_path = Path(scitex_root)
    dependencies = defaultdict(set)

    for module_dir in scitex_path.iterdir():
        if not module_dir.is_dir() or module_dir.name.startswith("_"):
            continue

        module_name = module_dir.name

        for py_file in module_dir.rglob("*.py"):
            imports = find_scitex_imports(py_file)
            for imp in imports:
                if imp != module_name:
                    dependencies[module_name].add(imp)

    return dependencies


@stx.session
def main(
    CONFIG=stx.session.INJECTED,
    logger=stx.session.INJECTED,
):
    """Analyze and print scitex module dependencies."""
    scitex_root = stx.path.find_git_root() / "src" / "scitex"
    deps = analyze_module_dependencies(scitex_root)

    print("Module Dependencies:")
    print("=" * 50)
    for module, imports in sorted(deps.items()):
        print(f"\n{module}:")
        for imp in sorted(imports):
            print(f"  - scitex.{imp}")

    return 0


if __name__ == "__main__":
    main()

# EOF
