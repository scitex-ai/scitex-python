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
        from scitex_dev.mcp_utils import wrap_as_mcp
        from scitex_notification._mcp.handlers import notify_handler

        return await wrap_as_mcp(
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
        from scitex_dev.mcp_utils import wrap_as_mcp
        from scitex_notification._mcp.handlers import get_config_handler

        return await wrap_as_mcp(
            get_config_handler,
            idempotent=True,
        )

    @mcp.tool()
    def ui_inspect_element(
        selector: str,
        timeout: int = 10,
    ) -> str:
        """Inspect a DOM element in the user's live browser by CSS selector.

        Returns computed styles, dimensions, parent chain, inline styles,
        and matching CSS rules. Essential for debugging CSS issues,
        verifying layout changes, and autonomous mobile responsive work.

        Standalone — works on any website open in playwright-cli browser.

        Parameters
        ----------
        selector : str
            CSS selector (e.g., '#ws-worktree-resizer', '.panel-resizer').
        timeout : int
            JS evaluation timeout in seconds (default: 10).

        Examples
        --------
        MCP: ui_inspect_element("#ws-worktree-resizer")
        MCP: ui_inspect_element(".stx-shell-sidebar.collapsed")
        """
        from scitex_dev.mcp_utils import wrap_as_mcp
        from scitex_ui._mcp.inspect import inspect_element_handler

        return wrap_as_mcp(
            inspect_element_handler,
            idempotent=True,
            selector=selector,
            timeout=timeout,
        )

    @mcp.tool()
    def ui_inspect_elements(
        selector: str,
        limit: int = 10,
        timeout: int = 10,
    ) -> str:
        """Inspect multiple DOM elements matching a CSS selector.

        Returns a summary of each matching element with key computed
        styles and dimensions. Use for bulk element inspection.

        Standalone — works on any website open in playwright-cli browser.

        Parameters
        ----------
        selector : str
            CSS selector (e.g., '.panel-resizer', '.stx-shell-sidebar').
        limit : int
            Maximum number of elements to return (default: 10).
        timeout : int
            JS evaluation timeout in seconds (default: 10).

        Examples
        --------
        MCP: ui_inspect_elements(".panel-resizer")
        MCP: ui_inspect_elements(".stx-shell-sidebar", limit=5)
        """
        from scitex_dev.mcp_utils import wrap_as_mcp
        from scitex_ui._mcp.inspect import inspect_elements_handler

        return wrap_as_mcp(
            inspect_elements_handler,
            idempotent=True,
            selector=selector,
            limit=limit,
            timeout=timeout,
        )


# EOF
