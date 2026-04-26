"""SciTeX repro — thin compatibility shim for scitex-repro.

Aliases ``scitex.repro`` to the standalone ``scitex_repro`` package via
``sys.modules`` so ``scitex.repro is scitex_repro`` and any new public name
added to scitex_repro is automatically visible.

Install: ``pip install scitex-repro``.
See: https://github.com/ywatanabe1989/scitex-repro
"""

import sys as _sys

try:
    import scitex_repro as _real
except ImportError as _e:  # pragma: no cover
    raise ImportError(
        "scitex.repro requires the 'scitex-repro' package. "
        "Install with: pip install scitex-repro"
    ) from _e

_sys.modules[__name__] = _real
