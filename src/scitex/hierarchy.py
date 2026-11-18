"""Umbrella-owned hierarchy declarations, independent of expert leaf slots.

Plain declarations need no SDK import. Explicit typed-record loading uses the
SDK contract when that capability is installed; it never duplicates validation.
"""

from __future__ import annotations

__all__ = ["get_hierarchy_declarations", "get_hierarchy_nodes"]

_DECLARATIONS = (
    {"id": "scitex", "index": "0", "label": "SciTeX", "parent_id": None},
    {"id": "scitex.main", "index": "1", "label": "Main", "parent_id": "scitex"},
    {
        "id": "package:scitex",
        "distribution": "scitex",
        "index": "1.1",
        "label": "scitex",
        "parent_id": "scitex.main",
    },
    {
        "id": "scitex.applications",
        "index": "2",
        "label": "Applications",
        "parent_id": "scitex",
    },
    {
        "id": "scitex.intermediate",
        "index": "3",
        "label": "Intermediate modules",
        "parent_id": "scitex",
    },
    {
        "id": "scitex.foundation",
        "index": "4",
        "label": "Lower-level modules",
        "parent_id": "scitex",
    },
)


def get_hierarchy_declarations() -> tuple[dict[str, str | None], ...]:
    """Return independent JSON-shaped copies of the six umbrella declarations.

    The root and four layers belong to the umbrella, along with its own package
    slot 1.1. Other leaves declare their own allocations. This is taxonomy, not
    dependencies, installed presence, permission or live availability.
    """
    return tuple(dict(node) for node in _DECLARATIONS)


def get_hierarchy_nodes() -> tuple[object, ...]:
    """Build the umbrella's six SDK HierarchyNode instances on explicit request.

    Requires the installed SDK hierarchy capability, not merely a matching
    version string. Metadata discovery and plain declaration access need no
    SDK. SDK owns node/tree validation; this function invents no leaf slots and
    performs no provider discovery, host admission or service operation.

    Raises
    ------
        RuntimeError: The SDK hierarchy module is not installed.
    """
    try:
        from scitex_sdk.hierarchy import HierarchyNode
    except ModuleNotFoundError as exc:
        if exc.name not in {"scitex_sdk", "scitex_sdk.hierarchy"}:
            raise
        raise RuntimeError(
            "Typed hierarchy records require the SDK hierarchy contract. "
            "Use get_hierarchy_declarations() to inspect metadata without it."
        ) from exc
    return tuple(HierarchyNode(**node) for node in get_hierarchy_declarations())
