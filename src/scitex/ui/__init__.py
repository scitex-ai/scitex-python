#!/usr/bin/env python3
# File: scitex/ui/__init__.py

"""scitex.ui — Deprecation shim. Use scitex.notify instead.

Notification backends have moved to scitex.notify.
This module provides backward-compatible wrappers that emit deprecation warnings.
"""

import warnings as _warnings


def _deprecated(name):
    _warnings.warn(
        f"scitex.ui.{name} is deprecated. Use scitex.notify.{name} instead.",
        DeprecationWarning,
        stacklevel=3,
    )


def alert(*args, **kwargs):
    _deprecated("alert")
    from scitex.notify import alert as _alert

    return _alert(*args, **kwargs)


def alert_async(*args, **kwargs):
    _deprecated("alert_async")
    from scitex.notify import alert_async as _alert_async

    return _alert_async(*args, **kwargs)


def available_backends():
    _deprecated("available_backends")
    from scitex.notify import available_backends as _available_backends

    return _available_backends()


__all__ = ["alert", "alert_async", "available_backends"]

# EOF
