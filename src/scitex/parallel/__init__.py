"""SciTeX parallel — thin compatibility shim for scitex-parallel.

Aliases ``scitex.parallel`` to the standalone ``scitex_parallel`` package via
``sys.modules`` so ``scitex.parallel is scitex_parallel`` and any new public name
added to scitex_parallel is automatically visible.

Install: ``pip install scitex-parallel``.
See: https://github.com/ywatanabe1989/scitex-parallel
"""

import sys as _sys

try:
    import scitex_parallel as _real
except ImportError as _e:  # pragma: no cover
    raise ImportError(
        "scitex.parallel requires the 'scitex-parallel' package. "
        "Install with: pip install scitex-parallel"
    ) from _e

_sys.modules[__name__] = _real
