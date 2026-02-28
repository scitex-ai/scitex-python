#!/usr/bin/env python3
# File: src/scitex/cli/tunnel.py
"""
SciTeX Tunnel CLI - Thin wrapper delegating to scitex-tunnel package.

All commands are delegated to scitex-tunnel CLI for maintainability.
"""

import subprocess
import sys

import click

# Check if scitex-tunnel package is available
try:
    import scitex_tunnel  # noqa: F401

    HAS_TUNNEL = True
except ImportError:
    HAS_TUNNEL = False


def _require_tunnel_pkg():
    """Check if scitex-tunnel package is available."""
    if not HAS_TUNNEL:
        click.secho(
            "scitex-tunnel package not installed. "
            "Install with: pip install scitex-tunnel",
            fg="red",
            err=True,
        )
        sys.exit(1)


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
    r"""SSH reverse tunnel for NAT traversal (delegates to scitex-tunnel).

    \b
    Commands (from scitex-tunnel):
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
      scitex-tunnel --help
    """
    _require_tunnel_pkg()

    # Delegate to scitex-tunnel CLI
    cmd = ["scitex-tunnel"] + list(args)
    sys.exit(subprocess.call(cmd))


# EOF
