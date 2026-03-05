#!/usr/bin/env python3
# File: scitex/_mcp_tools/tunnel.py
"""Tunnel tools for FastMCP unified server.

Delegates to scitex.tunnel (which delegates to scitex_tunnel).
"""

import json


def _json(data: dict) -> str:
    return json.dumps(data, indent=2, default=str)


def register_tunnel_tools(mcp) -> None:
    """Register tunnel tools with FastMCP server."""

    @mcp.tool()
    async def tunnel_setup(port: int, bastion_server: str, secret_key_path: str) -> str:
        """Set up a persistent SSH reverse tunnel.

        Creates an autossh systemd service for NAT traversal.
        The tunnel forwards a remote port on the bastion server
        back to the local machine's SSH port.
        """
        from scitex.tunnel import setup

        result = setup(port, bastion_server, secret_key_path)
        return _json(result)

    @mcp.tool()
    async def tunnel_remove(port: int) -> str:
        """Remove a persistent SSH reverse tunnel.

        Stops and disables the autossh systemd service for the given port.
        """
        from scitex.tunnel import remove

        result = remove(port)
        return _json(result)

    @mcp.tool()
    async def tunnel_status(port: int = 0) -> str:
        """Check status of SSH reverse tunnels.

        If port is 0 (default), shows all tunnel services.
        Otherwise shows status for the specific port.
        """
        from scitex.tunnel import status

        result = status(port if port else None)
        return _json(result)


# EOF
