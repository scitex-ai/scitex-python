"""Snapshot shared owner preferences before exposing any MCP adapter."""

from __future__ import annotations

import os
from collections.abc import Mapping
from dataclasses import dataclass
from types import MappingProxyType


def _namespace_key(namespace: str) -> str:
    return "SCITEX_MCP_USE_" + namespace.upper().replace("-", "_")


@dataclass(frozen=True)
class McpExposurePolicy:
    """Construction-time preferences, independent of CLI/Python and readiness."""

    owners: object
    disabled_namespaces: frozenset[str]

    def allows(self, owner: str, namespace: str) -> bool:
        """Require owner admission and the independently scoped namespace switch."""
        if isinstance(self.owners, Mapping):
            enabled = self.owners.get(owner, True)
        else:
            enabled = self.owners.is_enabled(owner, "mcp")
        return (
            bool(enabled) and _namespace_key(namespace) not in self.disabled_namespaces
        )


def load_package_policy(package_policy=None) -> McpExposurePolicy:
    """Reuse Dev's canonical resolver; never read a second preference store."""
    if isinstance(package_policy, McpExposurePolicy):
        return package_policy
    if package_policy is None:
        try:
            from scitex_dev.exposure import load_exposure_policy
        except ImportError as error:
            raise RuntimeError(
                "MCP owner policy requires scitex-dev.exposure.load_exposure_policy; "
                "install a SciTeX Dev release providing that public capability"
            ) from error
        package_policy = load_exposure_policy()
    elif isinstance(package_policy, Mapping):
        package_policy = MappingProxyType(dict(package_policy))
    if not isinstance(package_policy, Mapping) and not callable(
        getattr(package_policy, "is_enabled", None)
    ):
        raise TypeError(
            "package_policy must be a shared exposure snapshot or owner map"
        )
    disabled = frozenset(
        key
        for key, value in os.environ.items()
        if key.startswith("SCITEX_MCP_USE_") and value == "0"
    )
    return McpExposurePolicy(package_policy, disabled)


def is_exposed(owner: str, namespace: str, policy: McpExposurePolicy) -> bool:
    """Require both owner and namespace admission."""
    return policy.allows(owner, namespace)


def configure_discovery(server) -> None:
    """Reduce selected definitions using upstream search, without deferring imports."""
    mode = os.environ.get("SCITEX_MCP_DISCOVERY", "full")
    if mode not in {"full", "search"}:
        raise ValueError("SCITEX_MCP_DISCOVERY must be 'full' or 'search'")
    if mode == "full":
        return
    from scitex_dev.context import configure_mcp_discovery

    try:
        limit = int(os.environ.get("SCITEX_MCP_SEARCH_LIMIT", "5"))
    except ValueError as error:
        raise ValueError(
            "SCITEX_MCP_SEARCH_LIMIT must be a positive integer"
        ) from error
    configure_mcp_discovery(server, max_results=limit)
