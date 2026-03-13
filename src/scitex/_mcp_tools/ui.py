#!/usr/bin/env python3
# Timestamp: 2026-01-15
# File: /home/ywatanabe/proj/scitex-code/src/scitex/_mcp_tools/ui.py
"""UI module tools for FastMCP unified server."""

from typing import Optional


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
        from scitex_dev.mcp_utils import async_wrap_as_mcp

        from scitex.ui._mcp.handlers import notify_handler

        return await async_wrap_as_mcp(
            notify_handler,
            side_effects=["notification: sends desktop/system notification"],
            message=message,
            title=title,
            level=level,
            backend=backend,
            backends=backends,
            timeout=timeout,
        )

    @mcp.tool()
    async def ui_get_notification_config() -> str:
        """Get current notification configuration."""
        from scitex_dev.mcp_utils import async_wrap_as_mcp

        from scitex.ui._mcp.handlers import get_config_handler

        return await async_wrap_as_mcp(
            get_config_handler,
            idempotent=True,
        )


# EOF
