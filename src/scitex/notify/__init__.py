#!/usr/bin/env python3
"""SciTeX Notify — thin wrapper delegating to scitex-notification package.

All notification logic lives in the standalone scitex-notification package.
This module re-exports the public API for backward compatibility.
"""

from scitex_notification import (
    DEFAULT_FALLBACK_ORDER,
    alert,
    alert_async,
    available_backends,
    call,
    call_async,
    sms,
    sms_async,
)

__all__ = [
    "alert",
    "alert_async",
    "call",
    "call_async",
    "sms",
    "sms_async",
    "available_backends",
    "DEFAULT_FALLBACK_ORDER",
]

# EOF
