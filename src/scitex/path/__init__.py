"""SciTeX path — thin compatibility shim for scitex-path.

Aliases ``scitex.path`` to the standalone ``scitex_path`` package via
``sys.modules`` so ``scitex.path is scitex_path`` and any new public name
added to scitex_path is automatically visible.

Install: ``pip install scitex-path``.
See: https://github.com/ywatanabe1989/scitex-path
"""

import sys as _sys

try:
    import scitex_path as _real
except ImportError as _e:  # pragma: no cover
    raise ImportError(
        "scitex.path requires the 'scitex-path' package. "
        "Install with: pip install scitex-path"
    ) from _e

_sys.modules[__name__] = _real
