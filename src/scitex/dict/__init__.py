"""SciTeX dict — thin compatibility shim for scitex-dict.

Aliases ``scitex.dict`` to the standalone ``scitex_dict`` package via
``sys.modules`` so ``scitex.dict is scitex_dict`` and any new public name
added to scitex_dict is automatically visible.

Install: ``pip install scitex-dict``.
See: https://github.com/ywatanabe1989/scitex-dict
"""

import sys as _sys

try:
    import scitex_dict as _real
except ImportError as _e:  # pragma: no cover
    raise ImportError(
        "scitex.dict requires the 'scitex-dict' package. "
        "Install with: pip install scitex-dict"
    ) from _e

_sys.modules[__name__] = _real
