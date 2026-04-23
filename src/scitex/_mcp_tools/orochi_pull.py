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
        """Post a message to an Orochi IRC-like agent chat channel (e.g. `#general`, `#deploy`) — the multi-agent coordination bus used by scitex-orochi workflows. Drop-in replacement for manual `socket` + protocol framing, or shelling out to an IRC client. Use when an agent needs to notify peers, broadcast status, or coordinate with humans and other Claude instances via the shared Orochi room. `sender` defaults to hostname.

        Args:
            channel: Channel name (e.g. #general, #deploy)
            message: Message content to send
            sender: Sender name (defaults to hostname)
        """
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
        """Enumerate every agent (Claude instance, human, bot) currently connected to Orochi and the channels each one is in — peer-discovery for multi-agent coordination. Drop-in replacement for shelling into the Orochi server and running a `WHO`-style query. Use when an agent asks "who else is online?", "which agents can I delegate to?", "is the telegrammer agent up?", or before calling `orochi_send` to pick a recipient."""
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
        """Fetch the last N messages from an Orochi channel (default `#general`) — the scrollback buffer used to catch up on what other agents / humans said while offline. Drop-in replacement for custom log-tail scripts or IRC client history commands. Use when an agent joins a channel and asks "what did I miss?", "show recent activity in #deploy", "what was the last status report?", or is reconstructing context after a restart.

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
        """List every Orochi channel that has at least one connected agent — `ls /chat` for the agent coordination bus. Use when an agent asks "what channels are active?", "which rooms can I join?", "is there a #deploy channel?", or before calling `orochi_send` / `orochi_history` and needs to pick a target."""
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
