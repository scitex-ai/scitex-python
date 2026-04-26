"""SciTeX str — thin compatibility shim for scitex-str.

Aliases ``scitex.str`` to the standalone ``scitex_str`` package via
``sys.modules`` so ``scitex.str is scitex_str`` and any new public name
added to scitex_str is automatically visible.

Install: ``pip install scitex-str``.
See: https://github.com/ywatanabe1989/scitex-str
"""

import sys as _sys

try:
    import scitex_str as _real
except ImportError as _e:  # pragma: no cover
    raise ImportError(
        "scitex.str requires the 'scitex-str' package. "
        "Install with: pip install scitex-str"
    ) from _e

_sys.modules[__name__] = _real
