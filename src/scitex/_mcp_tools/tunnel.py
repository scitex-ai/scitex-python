#!/usr/bin/env python3
# File: scitex/_mcp_tools/tunnel.py
"""Tunnel tools for FastMCP unified server.

Delegates to scitex.tunnel (which delegates to scitex_tunnel).
"""


def register_tunnel_tools(mcp) -> None:
    """Register tunnel tools with FastMCP server."""

    @mcp.tool()
    async def tunnel_setup(port: int, bastion_server: str, secret_key_path: str) -> str:
        """Set up a persistent SSH reverse tunnel.

        Creates an autossh systemd service for NAT traversal.
        The tunnel forwards a remote port on the bastion server
        back to the local machine's SSH port.
        """
        from scitex_dev.mcp_utils import wrap_as_mcp

        from scitex.tunnel import setup

        return wrap_as_mcp(
            setup,
            port=port,
            bastion_server=bastion_server,
            secret_key_path=secret_key_path,
        )

    @mcp.tool()
    async def tunnel_remove(port: int) -> str:
        """Remove a persistent SSH reverse tunnel.

        Stops and disables the autossh systemd service for the given port.
        """
        from scitex_dev.mcp_utils import wrap_as_mcp

        from scitex.tunnel import remove

        return wrap_as_mcp(remove, port=port)

    @mcp.tool()
    async def tunnel_status(port: int = 0) -> str:
        """Check status of SSH reverse tunnels.

        If port is 0 (default), shows all tunnel services.
        Otherwise shows status for the specific port.
        """
        from scitex_dev.mcp_utils import wrap_as_mcp

        from scitex.tunnel import status

        return wrap_as_mcp(status, port=port if port else None)


# EOF
