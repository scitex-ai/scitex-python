#!/usr/bin/env python3
"""Find usage examples in codebase.

This example shows how to find real usage examples of functions
in test files and example directories.
"""

from scitex.introspect import find_examples


def example_find_usage():
    """Find usage examples in tests and examples."""
    print("=" * 60)
    print("1. Find Usage Examples")
    print("=" * 60)

    result = find_examples("scitex.introspect.get_signature", max_results=5)

    print(f"\nFound {result['count']} examples:")
    for ex in result["examples"]:
        print(f"\n--- {ex['file']}:{ex['line']} ---")
        # Print first few lines of context
        lines = ex["context"].split("\n")[:5]
        for line in lines:
            print(f"  {line}")
        if len(ex["context"].split("\n")) > 5:
            print("  ...")


def example_custom_search_paths():
    """Search in specific directories."""
    print("\n" + "=" * 60)
    print("2. Custom Search Paths")
    print("=" * 60)

    result = find_examples(
        "get_signature",
        search_paths=["tests/scitex/introspect"],
        max_results=3,
    )

    print(f"\nFound {result['count']} examples in tests:")
    for ex in result["examples"]:
        print(f"  - {ex['file']}:{ex['line']}")


if __name__ == "__main__":
    example_find_usage()
    example_custom_search_paths()
