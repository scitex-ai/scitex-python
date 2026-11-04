"""Honor the shared Dev package switches before resolving MCP providers."""

from __future__ import annotations

import os


def load_package_policy() -> dict[str, bool]:
    """Read the existing resolved configuration; never maintain another registry."""
    from scitex_dev import load_config

    return {package.name: package.mcp_enabled for package in load_config().packages}


def is_exposed(owner: str, namespace: str, policy: dict[str, bool]) -> bool:
    """A namespace environment switch cannot override a disabled package."""
    key = "SCITEX_MCP_USE_" + namespace.upper().replace("-", "_")
    return policy.get(owner, True) and os.environ.get(key, "1") != "0"


def configure_discovery(server) -> None:
    """Use Dev's thin upstream adapter only when explicitly requested."""
    mode = os.environ.get("SCITEX_MCP_DISCOVERY", "full")
    if mode not in {"full", "search"}:
        raise ValueError("SCITEX_MCP_DISCOVERY must be 'full' or 'search'")
    if mode == "full":
        return
    from scitex_dev.context import configure_mcp_discovery

    raw = os.environ.get("SCITEX_MCP_SEARCH_LIMIT", "5")
    try:
        limit = int(raw)
    except ValueError as error:
        raise ValueError(
            "SCITEX_MCP_SEARCH_LIMIT must be a positive integer"
        ) from error
    configure_mcp_discovery(server, max_results=limit)
