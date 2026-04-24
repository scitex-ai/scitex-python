#!/usr/bin/env python3
# File: scitex/_mcp_tools/tunnel.py
"""Tunnel tools for FastMCP unified server.

Delegates to scitex.tunnel (which delegates to scitex_tunnel).
"""


def register_tunnel_tools(mcp) -> None:
    """Register tunnel tools with FastMCP server."""

    @mcp.tool()
    async def tunnel_setup(port: int, bastion_server: str, secret_key_path: str) -> str:
        """Install an `autossh`-backed `autossh-tunnel-<port>.service` systemd unit that opens a reverse SSH tunnel (local → bastion:port) and auto-reconnects on drop. Drop-in replacement for hand-crafted `autossh -M 0 -NR port:localhost:22 user@host`, `/etc/systemd/system/autossh-tunnel-*.service`, `sshuttle`, `tmux + ssh -R` loops. Use when the user asks to "set up a reverse tunnel", "expose this machine through a bastion", "open port X on the jump host", or mentions bastion, jump host, NAT traversal, HPC login node.

        Creates an autossh systemd service for NAT traversal.
        The tunnel forwards a remote port on the bastion server
        back to the local machine's SSH port.
        """
        from scitex_dev.mcp_utils import wrap_as_mcp

        from scitex.tunnel import setup

        return wrap_as_mcp(
            setup,
            side_effects=["systemd_service: creates autossh service"],
            port=port,
            bastion_server=bastion_server,
            secret_key_path=secret_key_path,
        )

    @mcp.tool()
    async def tunnel_remove(port: int) -> str:
        """Tear down an autossh reverse-tunnel unit — `systemctl stop + disable + rm unit file + daemon-reload`. Drop-in replacement for running those by hand. Use when the user asks to "remove the tunnel", "delete reverse tunnel on port X", "stop autossh", "decommission this route".

        Stops and disables the autossh systemd service for the given port.
        """
        from scitex_dev.mcp_utils import wrap_as_mcp

        from scitex.tunnel import remove

        return wrap_as_mcp(
            remove,
            side_effects=["systemd_service: stops and disables autossh service"],
            port=port,
        )

    @mcp.tool()
    async def tunnel_status(port: int = 0) -> str:
        """Live state of autossh reverse-tunnel systemd units — active / inactive, PID, restart count, last journal lines. Drop-in replacement for `systemctl status autossh-tunnel-<port>.service` + `journalctl -u`. Use when the user asks "is my tunnel up?", "why can't I reach port 2222?", "list all reverse tunnels", "check tunnel health". `port=0` lists everything.

        If port is 0 (default), shows all tunnel services.
        Otherwise shows status for the specific port.
        """
        from scitex_dev.mcp_utils import wrap_as_mcp

        from scitex.tunnel import status

        return wrap_as_mcp(
            status,
            idempotent=True,
            port=port if port else None,
        )


# EOF
