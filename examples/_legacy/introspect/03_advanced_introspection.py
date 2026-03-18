#!/usr/bin/env python3
"""Advanced introspection - class hierarchy, type hints, and imports.

This example shows advanced introspection capabilities including
class inheritance analysis, type hint extraction, and import analysis.
"""

from scitex.introspect import (
    get_class_hierarchy,
    get_imports,
    get_mro,
    get_type_hints_detailed,
)


def example_class_hierarchy():
    """Get class inheritance hierarchy."""
    print("=" * 60)
    print("1. Class Hierarchy (MRO + Subclasses)")
    print("=" * 60)

    result = get_class_hierarchy("collections.abc.Mapping", max_depth=1)
    print("\nClass: collections.abc.Mapping")
    print(f"\nMRO ({result['mro_count']} classes):")
    for cls in result["mro"]:
        print(f"  {cls['qualname']}")

    print(f"\nDirect subclasses ({result['subclass_count']}):")
    for sub in result.get("subclasses", [])[:5]:
        print(f"  {sub['qualname']}")
    if result["subclass_count"] > 5:
        print(f"  ... and {result['subclass_count'] - 5} more")


def example_mro():
    """Get just the Method Resolution Order."""
    print("\n" + "=" * 60)
    print("2. Method Resolution Order (MRO)")
    print("=" * 60)

    result = get_mro("collections.OrderedDict")
    print("\nMRO of OrderedDict:")
    for name in result["mro"]:
        print(f"  {name}")


def example_type_hints():
    """Get detailed type hint analysis."""
    print("\n" + "=" * 60)
    print("3. Type Hints Analysis")
    print("=" * 60)

    result = get_type_hints_detailed("scitex.introspect._resolve.resolve_object")
    print(f"\nType hints ({result['hint_count']}):")
    for name, info in result.get("hints", {}).items():
        opt = " (optional)" if info.get("is_optional") else ""
        print(f"  {name}: {info['raw']}{opt}")
    if result.get("return_hint"):
        print(f"\nReturn: {result['return_hint']['raw']}")


def example_imports():
    """Get module imports (AST-based)."""
    print("\n" + "=" * 60)
    print("4. Module Imports (AST Analysis)")
    print("=" * 60)

    result = get_imports("scitex.introspect._resolve", categorize=True)
    print(f"\nImports ({result['import_count']}):")

    if result.get("categories"):
        for cat, imps in result["categories"].items():
            if imps:
                print(f"\n  [{cat}] ({len(imps)}):")
                for imp in imps[:3]:
                    print(f"    {imp['module']}")
                if len(imps) > 3:
                    print(f"    ... and {len(imps) - 3} more")


if __name__ == "__main__":
    example_class_hierarchy()
    example_mro()
    example_type_hints()
    example_imports()
