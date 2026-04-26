"""SciTeX pd — thin compatibility shim for scitex-pd.

Aliases ``scitex.pd`` to the standalone ``scitex_pd`` package via ``sys.modules``.
``scitex.pd is scitex_pd``.

Install: ``pip install scitex[pd]``  (or ``pip install scitex-pd``).
See: https://github.com/ywatanabe1989/scitex-pd
"""

import sys as _sys

try:
    import scitex_pd as _real
except ImportError as _e:  # pragma: no cover
    raise ImportError(
        "scitex.pd requires the 'scitex-pd' package. "
        "Install with: pip install scitex[pd]  (or: pip install scitex-pd)"
    ) from _e

_sys.modules[__name__] = _real
