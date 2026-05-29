#!/usr/bin/env python3
# File: scitex/tunnel/__init__.py

"""SciTeX Tunnel - SSH reverse tunnel for NAT traversal.

Tunnel functionality now ships in the ``scitex-ssh`` package (the former
standalone ``scitex-tunnel`` was merged into it). This module delegates
the reverse-tunnel API (``setup``/``remove``/``status``) to ``scitex_ssh``.
Install separately: pip install scitex-ssh

Architecture:
    scitex (hub) → stx.tunnel → scitex_ssh (spoke package)

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
    from scitex_ssh import AVAILABLE, get_version, remove, setup, status

    AVAILABLE = True
except ImportError as e:
    _import_error_msg = str(e)

    def _raise_import() -> None:
        raise ImportError(
            "scitex-ssh package not installed. "
            "Install with: pip install scitex-ssh\n"
            f"Original error: {_import_error_msg}"
        )

    def get_version() -> str:
        """Get scitex-ssh version (requires scitex-ssh package)."""
        _raise_import()

    def setup(port: int, bastion_server: str, secret_key_path: str) -> dict:
        """Set up reverse tunnel (requires scitex-ssh package)."""
        _raise_import()

    def remove(port: int) -> dict:
        """Remove reverse tunnel (requires scitex-ssh package)."""
        _raise_import()

    def status(port: int | None = None) -> dict:
        """Check tunnel status (requires scitex-ssh package)."""
        _raise_import()


# EOF
