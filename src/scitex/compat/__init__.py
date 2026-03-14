#!/usr/bin/env python3
# Timestamp: "2026-01-13 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex-code/src/scitex/compat/__init__.py

"""SciTeX Backward Compatibility Module.

This module provides aliases and wrappers for deprecated APIs.
Import from here to use old function names that delegate to new implementations.

Deprecation Timeline:
- v1.x: Old APIs work with deprecation warnings
- v2.x: Old APIs removed, use new APIs directly
"""

from __future__ import annotations

import warnings
from functools import wraps
from typing import Callable


def deprecated(new_name: str, removal_version: str = "2.0"):
    """Decorator to mark functions as deprecated."""

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            warnings.warn(
                f"{func.__name__} is deprecated. "
                f"Use {new_name} instead. "
                f"Will be removed in v{removal_version}.",
                DeprecationWarning,
                stacklevel=2,
            )
            return func(*args, **kwargs)

        return wrapper

    return decorator


# UI/Notification compatibility
def notify(*args, **kwargs):
    """Deprecated: Use scitex.notify.alert() instead."""
    warnings.warn(
        "scitex.compat.notify is deprecated. Use scitex.notify.alert instead.",
        DeprecationWarning,
        stacklevel=2,
    )
    from scitex.notify import alert

    return alert(*args, **kwargs)


async def notify_async(*args, **kwargs):
    """Deprecated: Use scitex.notify.alert_async() instead."""
    warnings.warn(
        "scitex.compat.notify_async is deprecated. Use scitex.notify.alert_async instead.",
        DeprecationWarning,
        stacklevel=2,
    )
    from scitex.notify import alert_async

    return await alert_async(*args, **kwargs)


__all__ = [
    "deprecated",
    "notify",
    "notify_async",
]


# EOF
