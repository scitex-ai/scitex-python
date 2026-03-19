#!/usr/bin/env python3
# Timestamp: "2026-01-13 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex-code/src/scitex/ui/mcp_server.py

"""MCP Server for SciTeX Notifications - Multi-backend alert system.

.. deprecated::
    This standalone server is deprecated. Use the unified scitex MCP server:
    CLI: scitex serve
    Python: from scitex.mcp_server import run_server

Supports: audio, desktop, email, matplotlib, playwright, webhook backends.
"""

from __future__ import annotations

import warnings

warnings.warn(
    "scitex.notification.mcp_server is deprecated. Use 'scitex serve' or "
    "'from scitex.mcp_server import run_server' for the unified MCP server.",
    DeprecationWarning,
    stacklevel=2,
)

import asyncio
from datetime import datetime

# Graceful MCP dependency handling
try:
    import mcp.types as types
    from mcp.server import NotificationOptions, Server
    from mcp.server.models import InitializationOptions
    from mcp.server.stdio import stdio_server

    MCP_AVAILABLE = True
except ImportError:
    MCP_AVAILABLE = False
    types = None  # type: ignore
    Server = None  # type: ignore
    NotificationOptions = None  # type: ignore
    InitializationOptions = None  # type: ignore
    stdio_server = None  # type: ignore

__all__ = ["NotifyServer", "main", "MCP_AVAILABLE"]


class NotifyServer:
    """MCP Server for multi-backend notifications."""

    def __init__(self):
        self.server = Server("scitex-ui")
        self._notification_count: int = 0
        self.setup_handlers()

    def setup_handlers(self):
        """Set up MCP server handlers."""
        from ._mcp.handlers import (
            available_backends_handler,
            get_config_handler,
            list_backends_handler,
            notify_by_level_handler,
            notify_handler,
        )
        from ._mcp.tool_schemas import get_tool_schemas

        @self.server.list_tools()
        async def handle_list_tools():
            return get_tool_schemas()

        @self.server.call_tool()
        async def handle_call_tool(name: str, arguments: dict):
            if name == "notify":
                self._notification_count += 1
                return await notify_handler(**arguments)
            elif name == "notify_by_level":
                self._notification_count += 1
                return await notify_by_level_handler(**arguments)
            elif name == "list_notification_backends":
                return await list_backends_handler()
            elif name == "available_notification_backends":
                return await available_backends_handler()
            elif name == "get_notification_config":
                return await get_config_handler()
            else:
                raise ValueError(f"Unknown tool: {name}")

        @self.server.list_resources()
        async def handle_list_resources():
            # Return notification statistics as a resource
            return [
                types.Resource(
                    uri="notify://stats",
                    name="Notification Statistics",
                    description="Current notification session statistics",
                    mimeType="application/json",
                )
            ]

        @self.server.read_resource()
        async def handle_read_resource(uri: str):
            if uri == "notify://stats":
                from ._backends import available_backends
                from ._backends._config import get_config

                config = get_config()
                stats = {
                    "total_notifications": self._notification_count,
                    "available_backends": available_backends(),
                    "default_backend": config.default_backend,
                    "timestamp": datetime.now().isoformat(),
                }
                import json

                return types.ResourceContent(
                    uri=uri,
                    mimeType="application/json",
                    content=json.dumps(stats, indent=2),
                )
            raise ValueError(f"Unknown resource: {uri}")


async def _run_server():
    """Run the MCP server (internal)."""
    server = NotifyServer()
    async with stdio_server() as (read_stream, write_stream):
        await server.server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="scitex-ui",
                server_version="0.1.0",
                capabilities=server.server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                ),
            ),
        )


def main():
    """Run the MCP server."""
    if not MCP_AVAILABLE:
        import sys

        print("=" * 60)
        print("MCP Server 'scitex-ui' requires the 'mcp' package.")
        print()
        print("Install with:")
        print("  pip install mcp")
        print()
        print("Or install scitex with MCP support:")
        print("  pip install scitex[mcp]")
        print("=" * 60)
        sys.exit(1)

    asyncio.run(_run_server())


if __name__ == "__main__":
    main()


# EOF
