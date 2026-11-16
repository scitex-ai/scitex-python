#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2026-01-08 01:56:48 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex-code/scripts/maintenance/dependencies/list_internal_imports.py


"""List internal imports within each scitex submodule."""

# Imports
import ast
from collections import defaultdict

import scitex as stx


# Functions and Classes
def find_internal_imports(file_path, module_name):
    """Extract internal imports within a module."""
    try:
        with open(file_path) as f:
            tree = ast.parse(f.read())
    except Exception:
        return []

    imports = []
    target_prefix = f"scitex.{module_name}"

    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom):
            if node.module and node.module.startswith(target_prefix):
                imports.append(node.module)
        elif isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name.startswith(target_prefix):
                    imports.append(alias.name)

    return imports


def analyze_internal_imports(scitex_path):
    """Analyze internal imports for each scitex submodule."""
    internal_imports = defaultdict(set)

    for module_dir in scitex_path.iterdir():
        if not module_dir.is_dir() or module_dir.name.startswith("_"):
            continue

        module_name = module_dir.name

        for py_file in module_dir.rglob("*.py"):
            imports = find_internal_imports(py_file, module_name)
            for imp in imports:
                internal_imports[module_name].add(imp)

    return internal_imports


@stx.session
def main(
    CONFIG=stx.session.INJECTED,
    logger=stx.session.INJECTED,
):
    """List internal imports within each scitex submodule."""
    scitex_root = stx.path.find_git_root() / "src" / "scitex"
    imports = analyze_internal_imports(scitex_root)

    print("Internal Imports by Module:")
    print("=" * 50)
    for module, module_imports in sorted(imports.items()):
        if module_imports:
            print(f"\n{module}:")
            for imp in sorted(module_imports):
                print(f"  - {imp}")

    return 0


if __name__ == "__main__":
    main()

# EOF
