"""SciTeX nn — thin compatibility shim for scitex-nn."""

import sys as _sys

try:
    import scitex_nn as _real
except ImportError as _e:
    raise ImportError(
        "scitex.nn requires the 'scitex-nn' package. "
        "Install with: pip install scitex[nn]  (or: pip install scitex-nn)"
    ) from _e

_sys.modules[__name__] = _real
