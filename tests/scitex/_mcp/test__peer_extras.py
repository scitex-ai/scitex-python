"""Real leaf ownership contracts for umbrella compatibility bridges."""

import inspect
import sys

import pytest


def test_social_bridge_matches_leaf_catalog_without_executing_handlers():
    """Compatibility names forward every actual leaf tool without invoking it."""
    # Arrange
    pytest.importorskip("socialia")
    from fastmcp import FastMCP
    from socialia._mcp import handlers
    from socialia._mcp.tools import register_all_tools
    from scitex._mcp import get_tools_sync
    from scitex._mcp._peer_extras import _register_social_core

    expected = FastMCP("owned-social-leaf-catalog")
    actual = FastMCP("owned-social-compatibility-catalog")
    codes = {
        value.__code__ for value in vars(handlers).values()
        if inspect.isfunction(value) and value.__module__ == handlers.__name__
    }
    calls = []
    previous = sys.getprofile()

    def record(frame, event, arg):
        if event == "call" and frame.f_code in codes:
            calls.append(frame.f_code.co_name)

    # Act
    sys.setprofile(record)
    try:
        register_all_tools(expected)
        _register_social_core(actual)
    finally:
        sys.setprofile(previous)
    observed = (set(get_tools_sync(actual)), calls)
    # Assert
    assert observed == (set(get_tools_sync(expected)), [])
