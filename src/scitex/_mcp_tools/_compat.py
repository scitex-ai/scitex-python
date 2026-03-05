#!/usr/bin/env python3
# Timestamp: 2026-02-23
# File: /home/ywatanabe/proj/scitex-code/src/scitex/_mcp_tools/_compat.py
"""FastMCP 2.x/3.x compatibility layer.

FastMCP 3.0 removed `_tool_manager` from the FastMCP object and renamed
`get_tools()` to `list_tools()` (returning a list instead of a dict).
This module provides a unified interface that works with both versions.
"""

import asyncio


def get_tools_sync(mcp_server, include_mounted: bool = True) -> dict:
    """Get all tools as {name: Tool} dict. Works with FastMCP 2.x and 3.x.

    FastMCP 2.x: _tool_manager.get_tools() (async, includes mounted servers)
                 or _tool_manager._tools (sync, local only)
    FastMCP 3.x: mcp.list_tools() (async, returns list, includes mounted)

    Args:
        mcp_server: FastMCP server instance.
        include_mounted: If True (default), include tools from mounted sub-servers.
            Set False for local-only tools (e.g., figrecipe bridge).
    """
    tm = getattr(mcp_server, "_tool_manager", None)

    # FastMCP 2.x local-only path (no async needed, fastest)
    if not include_mounted and tm is not None and hasattr(tm, "_tools"):
        return dict(tm._tools)

    # Async path for both 2.x (with mounted) and 3.x
    async def _gather():
        # FastMCP 2.x: _tool_manager.get_tools() returns dict with mounted
        if tm is not None and hasattr(tm, "get_tools"):
            return await tm.get_tools()
        # FastMCP 3.x: mcp.list_tools() returns list of Tool objects
        tools = await mcp_server.list_tools()
        return {t.name: t for t in tools}

    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = None

    if loop is not None and loop.is_running():
        import concurrent.futures

        with concurrent.futures.ThreadPoolExecutor() as pool:
            return pool.submit(asyncio.run, _gather()).result()
    return asyncio.run(_gather())


# EOF
