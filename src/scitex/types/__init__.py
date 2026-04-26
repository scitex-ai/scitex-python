"""SciTeX types — thin compatibility shim for scitex-types.

Aliases ``scitex.types`` to the standalone ``scitex_types`` package via
``sys.modules`` so ``scitex.types is scitex_types`` and any new public name
added to scitex_types is automatically visible.

Install: ``pip install scitex-types``.
See: https://github.com/ywatanabe1989/scitex-types
"""

import sys as _sys

try:
    import scitex_types as _real
except ImportError as _e:  # pragma: no cover
    raise ImportError(
        "scitex.types requires the 'scitex-types' package. "
        "Install with: pip install scitex-types"
    ) from _e

_sys.modules[__name__] = _real
