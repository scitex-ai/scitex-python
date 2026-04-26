"""SciTeX logging — thin compatibility shim for scitex-logging.

Aliases ``scitex.logging`` to the standalone ``scitex_logging`` package via
``sys.modules`` so ``scitex.logging is scitex_logging`` and every
sub-namespace + symbol resolves identically.

Install: ``pip install scitex-logging`` (already a core dep of ``scitex``).
See: https://github.com/ywatanabe1989/scitex-logging
"""

import sys as _sys

try:
    import scitex_logging as _real
except ImportError as _e:  # pragma: no cover
    raise ImportError(
        "scitex.logging requires the 'scitex-logging' package. "
        "Install with: pip install scitex-logging"
    ) from _e

_sys.modules[__name__] = _real
