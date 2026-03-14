#!/usr/bin/env python3
"""Notification module tools for FastMCP unified server."""

from typing import Optional


def register_notify_tools(mcp) -> None:
    """Register notification tools with FastMCP server."""

    @mcp.tool()
    async def notify_send(
        message: str,
        title: Optional[str] = None,
        level: str = "info",
        backend: Optional[str] = None,
        backends: Optional[list] = None,
        timeout: float = 5.0,
    ) -> str:
        """Send a notification via configured backends."""
        from scitex_dev.mcp_utils import async_wrap_as_mcp

        from scitex.notify._mcp.handlers import notify_handler

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
    async def notify_call(
        message: str,
        title: Optional[str] = None,
        level: str = "info",
        to_number: Optional[str] = None,
        repeat: int = 1,
        flow_sid: Optional[str] = None,
    ) -> str:
        """Make a phone call via Twilio to alert the user.

        Use repeat=2 to bypass iOS silent/manner mode (calls 30s apart).
        """
        from scitex_dev.mcp_utils import async_wrap_as_mcp

        from scitex.notify._mcp.handlers import notify_handler

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
    async def notify_sms(
        message: str,
        title: Optional[str] = None,
        to_number: Optional[str] = None,
    ) -> str:
        """Send an SMS via Twilio."""
        from scitex_dev.mcp_utils import async_wrap_as_mcp

        from scitex.notify._backends._twilio import send_sms

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
    async def notify_backends() -> str:
        """List all notification backends and their availability."""
        from scitex_dev.mcp_utils import async_wrap_as_mcp

        from scitex.notify._mcp.handlers import list_backends_handler

        return await async_wrap_as_mcp(
            list_backends_handler,
            idempotent=True,
        )

    @mcp.tool()
    async def notify_config() -> str:
        """Get current notification configuration."""
        from scitex_dev.mcp_utils import async_wrap_as_mcp

        from scitex.notify._mcp.handlers import get_config_handler

        return await async_wrap_as_mcp(
            get_config_handler,
            idempotent=True,
        )


# EOF
