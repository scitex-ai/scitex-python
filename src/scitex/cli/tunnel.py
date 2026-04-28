#!/usr/bin/env python3
# File: src/scitex/cli/tunnel.py
"""
SciTeX Tunnel CLI - Thin wrapper delegating to scitex-ssh package.

All commands are delegated to `scitex-ssh tunnel ...` (the tunnel subgroup
of the renamed scitex-ssh package, gated by ~/.scitex/ssh/config.yaml).
"""

import subprocess
import sys

import click

# Check if scitex-ssh package is available
try:
    import scitex_ssh  # noqa: F401

    HAS_TUNNEL = True
except ImportError:
    HAS_TUNNEL = False


def _require_tunnel_pkg():
    """Check if scitex-ssh package is available."""
    if not HAS_TUNNEL:
        click.secho(
            "scitex-ssh package not installed. Install with: pip install scitex-ssh",
            fg="red",
            err=True,
        )
        sys.exit(1)


_TUNNEL_COMMANDS = {
    "setup": "Set up a persistent SSH reverse tunnel",
    "remove": "Remove a persistent SSH reverse tunnel",
    "status": "Check status of SSH reverse tunnels",
}


@click.command(
    context_settings={
        "help_option_names": ["-h", "--help"],
        "ignore_unknown_options": True,
        "allow_extra_args": True,
        "allow_interspersed_args": False,
    },
)
@click.argument("args", nargs=-1, type=click.UNPROCESSED)
@click.pass_context
def tunnel(ctx, args):
    """SSH reverse tunnel for NAT traversal (delegates to `scitex-ssh tunnel`).

    \b
    Commands (from scitex-ssh tunnel):
      setup    Set up a persistent SSH reverse tunnel
      remove   Remove a persistent SSH reverse tunnel
      status   Check status of SSH reverse tunnels

    \b
    Examples:
      scitex tunnel setup -p 2222 -b bastion.example.com -s ~/.ssh/id_rsa
      scitex tunnel remove -p 2222
      scitex tunnel status
      scitex tunnel status -p 2222

    \b
    For full help:
      scitex tunnel --help
      scitex-ssh tunnel --help
    """
    args_list = list(args)

    if args_list == ["--json"]:
        from scitex_dev import Result

        click.echo(
            Result(
                success=True,
                data={"package": "scitex-ssh", "commands": _TUNNEL_COMMANDS},
            ).to_json()
        )
        return

    if not args_list:
        click.echo(ctx.get_help())
        return

    _require_tunnel_pkg()

    # Delegate to `scitex-ssh tunnel` CLI subgroup
    cmd = ["scitex-ssh", "tunnel"] + args_list
    sys.exit(subprocess.call(cmd))


# EOF
