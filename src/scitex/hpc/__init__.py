"""SciTeX hpc — thin compatibility shim for scitex-hpc."""

import sys as _sys

try:
    import scitex_hpc as _real
except ImportError as _e:
    raise ImportError(
        "scitex.hpc requires the 'scitex-hpc' package. "
        "Install with: pip install scitex[hpc]  (or: pip install scitex-hpc)"
    ) from _e

_sys.modules[__name__] = _real
