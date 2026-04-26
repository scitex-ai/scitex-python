"""SciTeX notification — thin compatibility shim for scitex-notification."""

import sys as _sys

try:
    import scitex_notification as _real
except ImportError as _e:
    raise ImportError(
        "scitex.notification requires the 'scitex-notification' package. "
        "Install with: pip install scitex[notification]  (or: pip install scitex-notification)"
    ) from _e

_sys.modules[__name__] = _real
