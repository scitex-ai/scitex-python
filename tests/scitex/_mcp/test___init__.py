#!/usr/bin/env python3
# Timestamp: 2026-05-31
# File: tests/scitex/test_mcp_entrypoint.py
"""Tests for the single umbrella MCP entrypoint (``scitex._mcp``).

The umbrella MCP server is a thin registry-mounting coordinator: it mounts
every non-archived peer's FastMCP under a brand-prefixed namespace and folds
in umbrella-only inline tools. These tests assert the collapse preserved
behavior:

* the unified server builds and exposes its public API,
* it mounts >0 peer servers with brand-prefix namespacing,
* tool-name renames (figrecipe fr_* -> plt_stx_*) and namespace aliases
  (crossref-local -> crossref) are applied,
* umbrella-only tool families survive,
* a missing optional peer does not crash the peer-extras registration.
"""

from __future__ import annotations

import pytest

fastmcp = pytest.importorskip("fastmcp")


def _entrypoint():
    """Return the scitex._mcp module, skipping if FastMCP is unavailable."""
    from scitex import _mcp

    if not _mcp.FASTMCP_AVAILABLE or _mcp.mcp is None:
        pytest.skip("umbrella MCP server not initialized")
    return _mcp


def _mounted_prefixes(mcp_server) -> set:
    """Namespaces of mounted peers — robust across FastMCP 2.x / 3.x."""
    from scitex._mcp import mounted_namespaces

    return mounted_namespaces(mcp_server)


def test_server_name_is_scitex():
    # Arrange
    _mcp = _entrypoint()
    # Act
    name = getattr(_mcp.mcp, "name", None)
    # Assert
    assert name == "scitex"


def test_public_api_exposes_main():
    # Arrange
    _mcp = _entrypoint()
    # Act
    has_main = callable(getattr(_mcp, "main", None))
    # Assert
    assert has_main is True


def test_public_api_exposes_run_server():
    # Arrange
    _mcp = _entrypoint()
    # Act
    has_run = callable(getattr(_mcp, "run_server", None))
    # Assert
    assert has_run is True


def test_mounts_more_than_zero_peers():
    # Arrange
    _mcp = _entrypoint()
    # Act
    prefixes = _mounted_prefixes(_mcp.mcp)
    # Assert
    assert len(prefixes) > 0


# Core peers are hard dependencies of the umbrella (pyproject [project]).
@pytest.mark.parametrize("peer", ["io", "stats", "scholar"])
def test_core_peer_mounted_with_brand_prefix(peer):
    # Arrange
    _mcp = _entrypoint()
    # Act
    prefixes = _mounted_prefixes(_mcp.mcp)
    # Assert
    assert peer in prefixes


def test_figrecipe_tools_renamed_to_plt_stx():
    # Arrange
    _mcp = _entrypoint()
    # Act
    local = set(_mcp.get_tools_sync(_mcp.mcp))
    # Assert
    assert any(n.startswith("plt_stx_") for n in local)


@pytest.mark.parametrize(
    "family",
    ["introspect", "usage", "docs", "skills", "template", "tunnel"],
)
def test_umbrella_only_family_present(family):
    # Arrange
    _mcp = _entrypoint()
    # Act
    local = set(_mcp.get_tools_sync(_mcp.mcp))
    # Assert
    assert any(n.startswith(family + "_") for n in local)


def _crossref_mounted() -> bool:
    """True when crossref-local (an optional extra) is importable + mounted."""
    _mcp = _entrypoint()
    return "crossref" in _mounted_prefixes(_mcp.mcp)


@pytest.mark.skipif(
    not _crossref_mounted(), reason="crossref-local (optional extra) not installed"
)
def test_crossref_namespace_alias_applied():
    # Arrange
    _mcp = _entrypoint()
    # Act
    prefixes = _mounted_prefixes(_mcp.mcp)
    # Assert
    assert "crossref-local" not in prefixes


def test_peer_extras_registration_folds_in_brand_renamed_tools():
    # Arrange
    from fastmcp import FastMCP

    from scitex._mcp import _peer_extras, get_tools_sync

    probe = FastMCP(name="probe")
    # Act
    _peer_extras.register_peer_extras(probe)
    local = set(get_tools_sync(probe))
    # Assert
    assert any(n.startswith("plt_stx_") for n in local)


# EOF
