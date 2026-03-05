#!/usr/bin/env python3
# Timestamp: 2026-01-15
# File: /home/ywatanabe/proj/scitex-code/src/scitex/_mcp_tools/ui.py
"""UI module tools for FastMCP unified server."""

import json
from typing import Optional


def _json(data: dict) -> str:
    return json.dumps(data, indent=2, default=str)


def register_ui_tools(mcp) -> None:
    """Register UI tools with FastMCP server."""

    @mcp.tool()
    async def ui_notify(
        message: str,
        title: Optional[str] = None,
        level: str = "info",
        backend: Optional[str] = None,
        backends: Optional[list] = None,
        timeout: float = 5.0,
    ) -> str:
        """Send a notification via configured backends."""
        from scitex.ui._mcp.handlers import notify_handler

        result = await notify_handler(
            message=message,
            title=title,
            level=level,
            backend=backend,
            backends=backends,
            timeout=timeout,
        )
        return _json(result)

    @mcp.tool()
    async def ui_get_notification_config() -> str:
        """Get current notification configuration."""
        from scitex.ui._mcp.handlers import get_config_handler

        result = await get_config_handler()
        return _json(result)


# EOF
