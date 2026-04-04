#!/usr/bin/env python3
"""SciTeX compat module — delegates to scitex-compat if available."""

from __future__ import annotations

import warnings
from functools import wraps
from typing import Callable

try:
    from scitex_compat import deprecated, notify, notify_async

    _BACKEND = "scitex-compat"
except ImportError:

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

    _BACKEND = "local"

__all__ = [
    "deprecated",
    "notify",
    "notify_async",
]

# EOF
