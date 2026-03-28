#!/usr/bin/env python3
"""Orochi agent communication tools for FastMCP unified server."""

from typing import Optional


def register_orochi_tools(mcp) -> None:
    """Register Orochi communication tools with FastMCP server."""

    @mcp.tool()
    async def orochi_send(
        channel: str,
        message: str,
        sender: Optional[str] = None,
    ) -> str:
        """Send a message to an Orochi channel.

        Args:
            channel: Channel name (e.g. #general, #deploy)
            message: Message content to send
            sender: Sender name (defaults to hostname)
        """
        import asyncio
        import platform

        # Lazy import to avoid import errors when orochi not installed
        try:
            from orochi.client import OrochiClient
        except ImportError:
            return "Error: scitex-orochi package not installed. Run: pip install -e ~/proj/scitex-orochi"

        name = sender or platform.node()
        client = OrochiClient(name, host=_get_host(), port=_get_port())
        try:
            await client.connect()
            await client.send(channel, message)
            await client.disconnect()
            return f"Sent to {channel}"
        except Exception as e:
            return f"Error: {e}"

    @mcp.tool()
    async def orochi_who() -> str:
        """List all agents currently connected to Orochi."""
        import json

        try:
            from orochi.client import OrochiClient
        except ImportError:
            return "Error: scitex-orochi package not installed"

        client = OrochiClient("query", host=_get_host(), port=_get_port())
        try:
            await client.connect()
            agents = await client.who()
            await client.disconnect()

            if not agents:
                return "No agents connected"

            lines = []
            for name, channels in agents.items():
                lines.append(f"  {name}: {', '.join(channels)}")
            return "Connected agents:\n" + "\n".join(lines)
        except Exception as e:
            return f"Error: {e}"

    @mcp.tool()
    async def orochi_history(
        channel: str = "#general",
        limit: int = 20,
    ) -> str:
        """Get recent message history from an Orochi channel.

        Args:
            channel: Channel name (default: #general)
            limit: Max messages to return (default: 20)
        """
        try:
            from orochi.client import OrochiClient
        except ImportError:
            return "Error: scitex-orochi package not installed"

        client = OrochiClient("query", host=_get_host(), port=_get_port())
        try:
            await client.connect()
            messages = await client.query_history(channel, limit=limit)
            await client.disconnect()

            if not messages:
                return f"No messages in {channel}"

            lines = []
            for m in messages:
                sender = m.get("sender", "?")
                content = m.get("content", "")
                ts = m.get("ts", "")
                if content:
                    lines.append(f"[{ts}] {sender}: {content}")
            return "\n".join(lines)
        except Exception as e:
            return f"Error: {e}"

    @mcp.tool()
    async def orochi_channels() -> str:
        """List all active Orochi channels."""
        try:
            from orochi.client import OrochiClient
        except ImportError:
            return "Error: scitex-orochi package not installed"

        client = OrochiClient("query", host=_get_host(), port=_get_port())
        try:
            await client.connect()
            agents = await client.who()
            await client.disconnect()

            channels = set()
            for chs in agents.values():
                channels.update(chs)

            if not channels:
                return "No active channels"
            return "Active channels:\n" + "\n".join(
                f"  {ch}" for ch in sorted(channels)
            )
        except Exception as e:
            return f"Error: {e}"


def _get_host() -> str:
    import os

    return os.environ.get("OROCHI_HOST", "192.168.0.102")


def _get_port() -> int:
    import os

    return int(os.environ.get("OROCHI_PORT", "9559"))


# EOF
