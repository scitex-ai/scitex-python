#!/usr/bin/env python3
"""SciTeX Agent Container CLI — re-exports as ``scitex agent-container``.

Single source of truth: ``scitex_agent_container.cli.main`` (the click.Group
exposed via the package's `cli` re-export shim).

Per general/03_interface_02_cli/05a_umbrella-passthrough.md (§5b).
"""

from __future__ import annotations

import click

try:
    from scitex_agent_container.cli import main as _ac_cli

    HAS_AC_PKG = True
except ImportError:
    HAS_AC_PKG = False
    _ac_cli = None


if HAS_AC_PKG:
    agent_container = _ac_cli
    agent_container.name = "agent-container"
else:

    @click.command(
        "agent-container",
        context_settings={"help_option_names": ["-h", "--help"]},
    )
    def agent_container():
        """scitex-agent-container is not installed."""
        click.secho(
            "scitex-agent-container package not installed. "
            "Install with: pip install scitex-agent-container",
            fg="red",
            err=True,
        )
        raise SystemExit(1)


# EOF
