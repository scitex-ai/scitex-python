"""SciTeX etc — thin compatibility shim for scitex-etc.

Aliases ``scitex.etc`` to the standalone ``scitex_etc`` package via
``sys.modules`` so ``scitex.etc is scitex_etc`` and any new public name
added to scitex_etc is automatically visible.

Install: ``pip install scitex-etc``.
See: https://github.com/ywatanabe1989/scitex-etc
"""

import sys as _sys

try:
    import scitex_etc as _real
except ImportError as _e:  # pragma: no cover
    raise ImportError(
        "scitex.etc requires the 'scitex-etc' package. "
        "Install with: pip install scitex-etc"
    ) from _e

_sys.modules[__name__] = _real
