#!/usr/bin/env python3
"""Call graph analysis with timeout protection.

This example shows how to analyze function call graphs,
which is useful for understanding code dependencies and flow.
"""

from scitex.introspect import get_call_graph, get_dependencies, get_function_calls


def example_function_calls():
    """Get calls made by a function."""
    print("=" * 60)
    print("1. Function Calls")
    print("=" * 60)

    result = get_function_calls("scitex.introspect._resolve.resolve_object")
    print("\nCalls made by resolve_object:")
    for call in result.get("calls", [])[:10]:
        print(f"  -> {call['name']} (line {call['line']})")


def example_call_graph():
    """Get call graph for a function with timeout."""
    print("\n" + "=" * 60)
    print("2. Call Graph (with timeout protection)")
    print("=" * 60)

    # Get call graph with 10 second timeout
    result = get_call_graph(
        "scitex.introspect._resolve.resolve_object",
        timeout_seconds=10,
        internal_only=False,
    )

    if result["success"]:
        print(f"\nCalls ({result.get('call_count', 0)}):")
        for call in result.get("calls", [])[:5]:
            print(f"  -> {call['name']}")

        print(f"\nCalled by ({result.get('caller_count', 0)}):")
        for caller in result.get("called_by", [])[:5]:
            print(f"  <- {caller['name']}")
    else:
        print(f"\nError: {result.get('error', 'Unknown')}")


def example_dependencies():
    """Get module dependencies."""
    print("\n" + "=" * 60)
    print("3. Module Dependencies")
    print("=" * 60)

    result = get_dependencies("scitex.introspect._resolve", recursive=False)
    print(f"\nDependencies ({result['dependency_count']}):")
    for dep in result.get("dependencies", [])[:10]:
        print(f"  {dep}")
    if result["dependency_count"] > 10:
        print(f"  ... and {result['dependency_count'] - 10} more")


if __name__ == "__main__":
    example_function_calls()
    example_call_graph()
    example_dependencies()
