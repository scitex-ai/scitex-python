"""SciTeX compat — thin compatibility shim for scitex-compat.

Aliases ``scitex.compat`` to the standalone ``scitex_compat`` package via
``sys.modules`` so ``scitex.compat is scitex_compat`` and any new public name
added to scitex_compat is automatically visible.

Install: ``pip install scitex-compat``.
See: https://github.com/ywatanabe1989/scitex-compat
"""

import sys as _sys

try:
    import scitex_compat as _real
except ImportError as _e:  # pragma: no cover
    raise ImportError(
        "scitex.compat requires the 'scitex-compat' package. "
        "Install with: pip install scitex-compat"
    ) from _e

_sys.modules[__name__] = _real
