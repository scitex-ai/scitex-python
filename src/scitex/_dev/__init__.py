"""SciTeX _dev — thin compatibility shim for scitex-dev."""

import sys as _sys

try:
    import scitex_dev as _real
except ImportError as _e:
    raise ImportError(
        "scitex._dev requires the 'scitex-dev' package. "
        "Install with: pip install scitex-dev"
    ) from _e

_sys.modules[__name__] = _real
