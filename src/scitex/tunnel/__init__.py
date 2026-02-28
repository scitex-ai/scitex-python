#!/usr/bin/env python3
# File: scitex/tunnel/__init__.py

"""SciTeX Tunnel - SSH reverse tunnel for NAT traversal.

This module delegates to the scitex-tunnel package (autossh-based tunnels).
Install separately: pip install scitex-tunnel

Architecture:
    scitex (hub) → stx.tunnel → scitex_tunnel (spoke package)

Example:
    >>> import scitex as stx
    >>> stx.tunnel.get_version()
    '0.1.0'
    >>> stx.tunnel.status()
    {'success': True, 'stdout': '...', 'stderr': ''}
"""

from __future__ import annotations

__all__ = [
    "setup",
    "remove",
    "status",
    "get_version",
    "AVAILABLE",
]

AVAILABLE = False
_import_error_msg = None

try:
    from scitex_tunnel import AVAILABLE, get_version, remove, setup, status

    AVAILABLE = True
except ImportError as e:
    _import_error_msg = str(e)

    def _raise_import() -> None:
        raise ImportError(
            "scitex-tunnel package not installed. "
            "Install with: pip install scitex-tunnel\n"
            f"Original error: {_import_error_msg}"
        )

    def get_version() -> str:
        """Get scitex-tunnel version (requires scitex-tunnel package)."""
        _raise_import()

    def setup(port: int, bastion_server: str, secret_key_path: str) -> dict:
        """Set up reverse tunnel (requires scitex-tunnel package)."""
        _raise_import()

    def remove(port: int) -> dict:
        """Remove reverse tunnel (requires scitex-tunnel package)."""
        _raise_import()

    def status(port: int | None = None) -> dict:
        """Check tunnel status (requires scitex-tunnel package)."""
        _raise_import()


# EOF
