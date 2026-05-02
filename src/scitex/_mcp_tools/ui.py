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
        """Send a UI-level alert through scitex-notification's multi-backend stack (audio TTS, desktop popup, emacs minibuffer, matplotlib banner, playwright toast, email, webhook, Telegram, Twilio) with automatic fallback. Drop-in replacement for `plyer.notification.notify`, ad-hoc `subprocess.run(['notify-send', ...])`, or browser `Notification` API. Use when the user asks to "notify from the UI", "alert me when this UI task finishes", "send a desktop notification from the scitex shell", or wires an app page to page the user."""
        from scitex_dev._mcp import wrap_as_mcp
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
        """Inspect the active scitex-notification config the UI will hand off to — fallback order, per-level backend routing (info/warning/error/critical), per-backend timeouts, credentials (redacted). Use when the user asks "which backends does ui_notify use?", "show UI notification config", or is debugging a silent `ui_notify` call."""
        from scitex_dev._mcp import wrap_as_mcp
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
        """Introspect one DOM element in the user's live playwright-cli browser — returns tag, id, classes, every attribute, bounding box, key computed styles (display / position / flex / width / height / margin / padding / z-index / overflow / background), inline `style.cssText`, 5-level parent chain, and all matching CSS rules with their source stylesheet. Drop-in replacement for hand-rolled `playwright.evaluate("getComputedStyle(...)")` JS blobs, Chrome DevTools `Elements → Computed` copy-pasting, and `document.querySelector` in the browser console. Use whenever the user asks to "inspect this element", "why isn't this styled?", "check computed width of #foo", "debug CSS for .bar", "verify my layout change", "is this hidden by overflow?", or is iterating on CSS / responsive design.

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
        from scitex_dev._mcp import wrap_as_mcp
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
        """Introspect every element matching a CSS selector in the user's live playwright-cli browser — returns total count + per-element summary (tag, id, classes, key computed styles, bounding rect, inline style, parent descriptor), capped by `limit`. Drop-in replacement for `document.querySelectorAll(...).forEach(el => el.getBoundingClientRect())` console loops. Use whenever the user asks to "list all .panel-resizer elements", "how many sidebars are rendered?", "check sizes of all app-card nodes", "audit every .stx-shell-* child", or is hunting for duplicate/misaligned elements.

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
        from scitex_dev._mcp import wrap_as_mcp
        from scitex_ui._mcp.inspect import inspect_elements_handler

        return wrap_as_mcp(
            inspect_elements_handler,
            idempotent=True,
            selector=selector,
            limit=limit,
            timeout=timeout,
        )


# EOF
