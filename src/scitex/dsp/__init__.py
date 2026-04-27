"""SciTeX dsp — thin compatibility shim for scitex-dsp."""

import sys as _sys

try:
    import scitex_dsp as _real
except ImportError as _e:
    raise ImportError(
        "scitex.dsp requires the 'scitex-dsp' package. "
        "Install with: pip install scitex[dsp]  (or: pip install scitex-dsp)"
    ) from _e

_sys.modules[__name__] = _real
