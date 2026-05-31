#!/usr/bin/env python3
# Timestamp: 2026-05-31
# File: src/scitex/_mcp/_compat.py
"""FastMCP 2.x/3.x compatibility layer.

FastMCP 3.0 removed `_tool_manager` from the FastMCP object and renamed
`get_tools()` to `list_tools()` (returning a list instead of a dict).
This module provides a unified interface that works with both versions.
"""

import asyncio

__all__ = ["get_tools_sync", "safe_mount", "mounted_namespaces"]


def mounted_namespaces(mcp_server) -> set:
    """Namespaces of every mounted peer sub-server. Works on FastMCP 2.x & 3.x.

    FastMCP 2.x exposes mounted sub-servers via ``_mounted_servers`` (each with
    a ``prefix``/``namespace``) and resolves their tools lazily — so the parent
    ``get_tools`` does NOT include them.

    FastMCP 3.x folds mounted tools into ``list_tools()`` directly (no stable
    ``_mounted_servers`` attribute), so the namespace is the ``<ns>_`` prefix on
    each mounted tool name.

    We union both signals so the same call yields the mounted peer namespaces
    regardless of FastMCP major version.
    """
    namespaces = set()

    # FastMCP 2.x: explicit mounted-server records.
    for srv in getattr(mcp_server, "_mounted_servers", []) or []:
        ns = getattr(srv, "prefix", None) or getattr(srv, "namespace", None)
        if ns:
            namespaces.add(ns)

    # FastMCP 3.x (and any version): prefixes on resolvable tool names. A
    # mounted tool is ``<namespace>_<tool>``; the umbrella's own local tools
    # also share this shape, so this can include a few umbrella-only prefixes
    # (introspect, usage, ...). Callers asserting on peer namespaces should
    # check membership, not exact equality.
    for name in get_tools_sync(mcp_server):
        if "_" in name:
            namespaces.add(name.split("_", 1)[0])

    return namespaces


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


def safe_mount(mcp, sub_server, namespace=None, prefix=None):
    """Mount a sub-server with namespace/prefix compatibility.

    FastMCP 2.x uses `prefix` parameter.
    FastMCP 3.x renamed it to `namespace`.
    This function tries both, handling the API difference.

    Args:
        mcp: Parent FastMCP server.
        sub_server: FastMCP sub-server to mount.
        namespace: Namespace/prefix string (e.g., "stats").
        prefix: Alias for namespace (legacy).
    """
    name = namespace or prefix
    import inspect

    sig = inspect.signature(mcp.mount)
    params = sig.parameters

    if "namespace" in params:
        mcp.mount(sub_server, namespace=name)
    elif "prefix" in params:
        mcp.mount(sub_server, prefix=name)
    else:
        # Fallback: try positional
        mcp.mount(sub_server, name)


# EOF
