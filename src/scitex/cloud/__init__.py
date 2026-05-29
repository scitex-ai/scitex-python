#!/usr/bin/env python3
# Timestamp: 2026-02-05
# File: scitex/cloud/__init__.py

"""SciTeX Cloud - Web service integration.

This module delegates to the ``scitex-hub`` package (Django web
application; formerly ``scitex-cloud``). Install separately:
pip install scitex-hub

Architecture:
    scitex (hub) → stx.cloud → scitex_hub (spoke package)

Example:
    >>> import scitex as stx
    >>> stx.cloud.get_version()
    '0.18.0'
    >>> stx.cloud.health_check()
    {'status': 'healthy', ...}
"""

from __future__ import annotations

__all__ = [
    "get_version",
    "health_check",
    "get_context",
    "eval_js",
    "ui_action",
    "AVAILABLE",
]

AVAILABLE = False
_import_error_msg = None

try:
    from scitex_hub import CloudClient as _Client
    from scitex_hub import get_version, health_check

    def get_context(page: str = "", **kw) -> dict:
        """Get web app context: username, page, skills, available actions."""
        return _Client(**kw).get_context(page)

    def eval_js(code: str, timeout: int = 10, **kw) -> dict:
        """Evaluate JavaScript in user's browser."""
        return _Client(**kw).eval_js(code, timeout)

    def ui_action(steps: list, delay_ms: int = 900, **kw) -> dict:
        """Drive browser UI: navigate, highlight, click, fill, scroll."""
        return _Client(**kw).ui_action(steps, delay_ms)

    AVAILABLE = True
except ImportError as e:
    _import_error_msg = str(e)

    def _raise_import() -> None:
        raise ImportError(
            "scitex-hub package not installed. "
            "Install with: pip install scitex-hub\n"
            f"Original error: {_import_error_msg}"
        )

    def get_version() -> str:
        """Get scitex-hub version (requires scitex-hub package)."""
        _raise_import()

    def health_check() -> dict:
        """Check scitex-hub health (requires scitex-hub package)."""
        _raise_import()

    def get_context(page: str = "", **kw) -> dict:
        """Get web app context (requires scitex-hub package)."""
        _raise_import()

    def eval_js(code: str, timeout: int = 10, **kw) -> dict:
        """Evaluate JS in browser (requires scitex-hub package)."""
        _raise_import()

    def ui_action(steps: list, delay_ms: int = 900, **kw) -> dict:
        """Drive browser UI (requires scitex-hub package)."""
        _raise_import()


# EOF
