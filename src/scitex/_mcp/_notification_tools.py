#!/usr/bin/env python3
# Timestamp: 2026-05-31
# File: src/scitex/_mcp/_notification_tools.py
"""Notification MCP tools (scitex_notification handlers).

Umbrella-only family — wraps the multi-backend notifier so the unified
server exposes notify / call / sms / backends / config tools.
"""

from __future__ import annotations

from typing import Optional

__all__ = ["register_notification_tools"]


def register_notification_tools(mcp) -> None:
    """Register every notification_* tool onto the FastMCP server."""

    @mcp.tool()
    async def notification_send(
        message: str,
        title: Optional[str] = None,
        level: str = "info",
        backend: Optional[str] = None,
        backends: Optional[list] = None,
        timeout: float = 5.0,
    ) -> str:
        """Send an alert through any of 9 backends — audio (TTS), desktop popup, emacs minibuffer, matplotlib banner, playwright browser toast, email (SMTP), webhook (HTTP POST), Telegram, Twilio phone/SMS — with automatic fallback. Use whenever the user asks to "notify me", "alert me when this finishes", "beep when done", "email me the result", "ping me on Telegram"."""
        from scitex_dev.ecosystem import async_wrap_as_mcp
        from scitex_notification._mcp.handlers import notify_handler

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
    async def notification_call(
        message: str,
        title: Optional[str] = None,
        level: str = "info",
        to_number: Optional[str] = None,
        repeat: int = 1,
        flow_sid: Optional[str] = None,
    ) -> str:
        """Place an actual Twilio phone call to the user that reads `message` via TTS — bypasses DND/Focus when iOS Emergency Bypass / Repeated Calls is configured (`repeat=2`). Use whenever the user asks to "call my phone", "wake me up when this fails", "escalate to a phone call on critical errors", "page me if the server dies"."""
        from scitex_dev.ecosystem import async_wrap_as_mcp
        from scitex_notification._mcp.handlers import notify_handler

        kwargs = {"repeat": repeat}
        if to_number:
            kwargs["to_number"] = to_number
        if flow_sid:
            kwargs["flow_sid"] = flow_sid
        return await async_wrap_as_mcp(
            notify_handler,
            side_effects=["phone_call: makes a phone call via Twilio"],
            message=message,
            title=title,
            level=level,
            backend="twilio",
            timeout=120.0,
            **kwargs,
        )

    @mcp.tool()
    async def notification_sms(
        message: str,
        title: Optional[str] = None,
        to_number: Optional[str] = None,
    ) -> str:
        """Send an SMS to the user via Twilio — text-only alternative to `notification_call`. Use whenever the user asks to "text me", "SMS me the build result", "send a text when done"."""
        from scitex_dev.ecosystem import async_wrap_as_mcp
        from scitex_notification._backends._twilio import send_sms

        kwargs = {}
        if to_number:
            kwargs["to_number"] = to_number
        return await async_wrap_as_mcp(
            send_sms,
            side_effects=["sms: sends an SMS message via Twilio"],
            message=message,
            title=title,
            **kwargs,
        )

    @mcp.tool()
    async def notification_backends() -> str:
        """Enumerate every registered notification backend with reachability status — deps installed, env vars set, credentials valid. Use when the user asks "which notifiers are set up?", "why isn't my Twilio alert working?", "is email configured?"."""
        from scitex_dev.ecosystem import async_wrap_as_mcp
        from scitex_notification._mcp.handlers import list_backends_handler

        return await async_wrap_as_mcp(list_backends_handler, idempotent=True)

    @mcp.tool()
    async def notification_config() -> str:
        """Dump the active notification config — fallback order, per-level backend mapping, per-backend timeouts, credentials (secrets redacted). Use when the user asks "show my notification config", "what's my fallback order?", "which backends fire for critical?"."""
        from scitex_dev.ecosystem import async_wrap_as_mcp
        from scitex_notification._mcp.handlers import get_config_handler

        return await async_wrap_as_mcp(get_config_handler, idempotent=True)


# EOF
