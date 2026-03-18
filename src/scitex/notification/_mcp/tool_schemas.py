#!/usr/bin/env python3
# Timestamp: "2026-01-13 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex-code/src/scitex/ui/_mcp/tool_schemas.py

"""Tool schemas for the scitex-notify MCP server."""

from __future__ import annotations

import mcp.types as types

__all__ = ["get_tool_schemas"]


def get_tool_schemas() -> list[types.Tool]:
    """Return all tool schemas for the notification MCP server."""
    return [
        types.Tool(
            name="notify",
            description=(
                "Send a notification via configured backends (audio, desktop, email, "
                "matplotlib, playwright, webhook). Supports multi-backend delivery "
                "and notification levels (info, warning, error, critical)."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "message": {
                        "type": "string",
                        "description": "The notification message to send",
                    },
                    "title": {
                        "type": "string",
                        "description": "Optional notification title",
                    },
                    "level": {
                        "type": "string",
                        "description": "Notification urgency level",
                        "enum": ["info", "warning", "error", "critical"],
                        "default": "info",
                    },
                    "backend": {
                        "type": "string",
                        "description": (
                            "Backend to use (audio, desktop, email, matplotlib, "
                            "playwright, webhook). If not specified, uses default from config."
                        ),
                    },
                    "backends": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Multiple backends to use simultaneously",
                    },
                    "timeout": {
                        "type": "number",
                        "description": "Timeout for visual backends (matplotlib, playwright)",
                        "default": 5.0,
                    },
                },
                "required": ["message"],
            },
        ),
        types.Tool(
            name="notify_by_level",
            description=(
                "Send notification using backends configured for a specific level. "
                "Uses level_backends config (e.g., critical -> audio + desktop + email)."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "message": {
                        "type": "string",
                        "description": "The notification message to send",
                    },
                    "title": {
                        "type": "string",
                        "description": "Optional notification title",
                    },
                    "level": {
                        "type": "string",
                        "description": "Notification level (determines which backends to use)",
                        "enum": ["info", "warning", "error", "critical"],
                        "default": "info",
                    },
                },
                "required": ["message"],
            },
        ),
        types.Tool(
            name="list_notification_backends",
            description="List all notification backends and their status",
            inputSchema={"type": "object", "properties": {}},
        ),
        types.Tool(
            name="available_notification_backends",
            description="Get list of currently available (working) notification backends",
            inputSchema={"type": "object", "properties": {}},
        ),
        types.Tool(
            name="get_notification_config",
            description="Get current notification configuration (priority, level_backends, timeouts)",
            inputSchema={"type": "object", "properties": {}},
        ),
    ]


# EOF
