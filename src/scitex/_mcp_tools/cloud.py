#!/usr/bin/env python3
# Timestamp: 2026-02-26
# File: scitex/_mcp_tools/cloud.py
"""Cloud context tools for FastMCP unified server.

Delegates to scitex.cloud (which delegates to scitex_cloud.CloudClient).
"""

import json


def _json(data: dict) -> str:
    return json.dumps(data, indent=2, default=str)


def register_cloud_tools(mcp) -> None:
    """Register cloud context/UI tools with FastMCP server."""

    @mcp.tool()
    async def cloud_get_context(page: str = "") -> str:
        """[cloud] Get web app page context, skills, and available actions.

        Returns the current user, active skill for the page, all registered
        app skills, available UI actions, and media rendering capabilities.
        """
        from scitex.cloud import get_context

        result = get_context(page)
        return _json(result)

    @mcp.tool()
    async def cloud_eval_js(code: str, timeout: int = 10) -> str:
        """[cloud] Evaluate JavaScript in user's browser.

        Sends JS code to the user's browser via WebSocket relay,
        waits for the evaluation result, and returns it.
        Timeout is capped at 30 seconds server-side.
        """
        from scitex.cloud import eval_js

        result = eval_js(code, timeout)
        return _json(result)

    @mcp.tool()
    async def cloud_ui_action(steps: list, delay_ms: int = 900) -> str:
        """[cloud] Drive browser UI (navigate, highlight, click, fill, scroll).

        Steps is a list of action dicts, e.g.:
        [{"action": "navigate", "url": "/writer/"},
         {"action": "click", "selector": "#save-btn"}]
        """
        from scitex.cloud import ui_action

        result = ui_action(steps, delay_ms)
        return _json(result)


# EOF
