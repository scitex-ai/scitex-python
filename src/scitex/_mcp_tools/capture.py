#!/usr/bin/env python3
# Timestamp: 2026-01-15
# File: /home/ywatanabe/proj/scitex-code/src/scitex/_mcp_tools/capture.py
"""Capture module tools for FastMCP unified server."""

import json
from typing import Optional


def _json(data: dict) -> str:
    return json.dumps(data, indent=2, default=str)


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
        """Capture screenshot - monitor, window, browser, or everything."""
        from scitex.capture._mcp.handlers import capture_screenshot_handler

        result = await capture_screenshot_handler(
            monitor_id=monitor_id,
            all=all,
            quality=quality,
            message=message,
            return_base64=return_base64,
            url=url,
            app=app,
        )
        return _json(result)


# EOF
