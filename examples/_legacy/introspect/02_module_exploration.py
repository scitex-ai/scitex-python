#!/usr/bin/env python3
"""Module exploration examples - listing members and exports.

This example shows how to explore Python modules and classes using
scitex.introspect, similar to Python's dir() but with more detail.
"""

from scitex.introspect import get_exports, list_members


def example_list_members():
    """List members of a module (like dir())."""
    print("=" * 60)
    print("1. List Members (like dir())")
    print("=" * 60)

    # List public functions in json module
    result = list_members("json", filter="public", kind="functions")
    print(f"\nPublic functions in json ({result['count']}):")
    for m in result["members"]:
        summary = f" - {m['summary']}" if m["summary"] else ""
        print(f"  {m['name']}{summary}")


def example_list_class_members():
    """List members of a class."""
    print("\n" + "=" * 60)
    print("2. List Class Members")
    print("=" * 60)

    # List public methods of pathlib.Path
    result = list_members("pathlib.Path", filter="public", kind="functions")
    print(f"\nPublic methods of pathlib.Path ({result['count']}):")
    for m in result["members"][:10]:  # First 10
        print(f"  {m['name']}")
    if result["count"] > 10:
        print(f"  ... and {result['count'] - 10} more")


def example_exports():
    """Get __all__ exports."""
    print("\n" + "=" * 60)
    print("3. Get __all__ Exports")
    print("=" * 60)

    result = get_exports("json")
    status = "defined" if result["has_all"] else "not defined"
    print(f"\n__all__ is {status}")
    print(f"Exports ({result['count']}):")
    for name in result["exports"]:
        print(f"  {name}")


def example_filter_types():
    """Filter members by different criteria."""
    print("\n" + "=" * 60)
    print("4. Filter by Type")
    print("=" * 60)

    # Classes only
    result = list_members("pathlib", kind="classes", filter="public")
    print(f"\nClasses in pathlib ({result['count']}):")
    for m in result["members"]:
        print(f"  {m['name']}")


if __name__ == "__main__":
    example_list_members()
    example_list_class_members()
    example_exports()
    example_filter_types()
