"""SciTeX capture — thin compatibility shim for scitex-capture.

Aliases ``scitex.capture`` to the standalone ``scitex_capture`` package via
``sys.modules``. ``scitex.capture is scitex_capture``.

Install: ``pip install scitex[capture]``  (or ``pip install scitex-capture``).
See: https://github.com/ywatanabe1989/scitex-capture
"""

import sys as _sys

try:
    import scitex_capture as _real
except ImportError as _e:  # pragma: no cover
    raise ImportError(
        "scitex.capture requires the 'scitex-capture' package. "
        "Install with: pip install scitex[capture]  (or: pip install scitex-capture)"
    ) from _e

_sys.modules[__name__] = _real
