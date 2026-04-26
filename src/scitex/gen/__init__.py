"""SciTeX gen — thin compatibility shim for scitex-gen."""

import sys as _sys

try:
    import scitex_gen as _real
except ImportError as _e:
    raise ImportError(
        "scitex.gen requires the 'scitex-gen' package. "
        "Install with: pip install scitex[gen]  (or: pip install scitex-gen)"
    ) from _e

_sys.modules[__name__] = _real
