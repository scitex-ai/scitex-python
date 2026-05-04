#!/usr/bin/env python3
# Timestamp: 2026-01-15
# File: /home/ywatanabe/proj/scitex-code/src/scitex/_mcp_tools/capture.py
"""Capture module tools for FastMCP unified server."""

from typing import Optional


def register_capture_tools(mcp) -> None:
    """Register capture tools with FastMCP server."""

    @mcp.tool()
    async def capture_screenshot(
        monitor_id: int = 0,
        all: bool = False,
        quality: int = 85,
        message: Optional[str] = None,
        return_base64: bool = False,
        url: Optional[str] = None,
        app: Optional[str] = None,
    ) -> str:
        """Take a JPEG screenshot of a chosen target — a specific monitor (`monitor_id=N`), every monitor at once (`all=True`), a live browser tab (`url=...`), or an X11 application window (`app='emacs'`). Drop-in replacement for `scrot`, `gnome-screenshot`, `maim`, `mss.mss().shot()`, and ad-hoc `playwright.screenshot()`. Use when the user asks to "take a screenshot", "capture my screen", "grab a picture of the browser", "screenshot that app window", "prove visually this is fixed", or is attaching UI evidence to a bug report / review. `return_base64=True` inlines instead of saving."""
        from scitex_dev.ecosystem import async_wrap_as_mcp

        from scitex.capture._mcp.handlers import capture_screenshot_handler

        return await async_wrap_as_mcp(
            capture_screenshot_handler,
            side_effects=["file_create: screenshot image file"],
            idempotent=True,
            monitor_id=monitor_id,
            all=all,
            quality=quality,
            message=message,
            return_base64=return_base64,
            url=url,
            app=app,
        )


# EOF
