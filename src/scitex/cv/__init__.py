"""SciTeX cv — thin compatibility shim for scitex-cv.

Aliases ``scitex.cv`` to the standalone ``scitex_cv`` package via ``sys.modules``.
``scitex.cv is scitex_cv``.

Install: ``pip install scitex[cv]``  (or ``pip install scitex-cv``).
See: https://github.com/ywatanabe1989/scitex-cv
"""

import sys as _sys

try:
    import scitex_cv as _real
except ImportError as _e:  # pragma: no cover
    raise ImportError(
        "scitex.cv requires the 'scitex-cv' package. "
        "Install with: pip install scitex[cv]  (or: pip install scitex-cv)"
    ) from _e

_sys.modules[__name__] = _real
