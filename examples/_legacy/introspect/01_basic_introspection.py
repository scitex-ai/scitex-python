#!/usr/bin/env python3
"""Basic introspection examples - signatures, docstrings, and source code.

This example shows how to use scitex.introspect for IPython-like introspection
of any Python package.
"""

from scitex.introspect import get_docstring, get_signature, get_source


def example_signature():
    """Get function signature (like IPython's func?)."""
    print("=" * 60)
    print("1. Get Signature (like func?)")
    print("=" * 60)

    # Get signature of json.dumps
    result = get_signature("json.dumps")
    print(f"\nSignature: {result['signature']}")
    print("\nParameters:")
    for p in result["parameters"]:
        line = f"  {p['name']}"
        if "annotation" in p:
            line += f": {p['annotation']}"
        if "default" in p:
            line += f" = {p['default']}"
        print(line)


def example_docstring():
    """Get docstring in various formats."""
    print("\n" + "=" * 60)
    print("2. Get Docstring")
    print("=" * 60)

    # Raw docstring
    result = get_docstring("json.dumps", format="raw")
    print(f"\nRaw docstring (first 200 chars):\n{result['docstring'][:200]}...")

    # Summary only
    result = get_docstring("json.dumps", format="summary")
    print(f"\nSummary: {result['docstring']}")


def example_source():
    """Get source code (like IPython's func??)."""
    print("\n" + "=" * 60)
    print("3. Get Source Code (like func??)")
    print("=" * 60)

    # Get source with line limit
    result = get_source("scitex.introspect._resolve.resolve_object", max_lines=10)
    print(f"\nFile: {result['file']}:{result['line_start']}")
    print(f"Lines: {result['line_count']}")
    print(f"\nSource:\n{result['source']}")


if __name__ == "__main__":
    example_signature()
    example_docstring()
    example_source()
