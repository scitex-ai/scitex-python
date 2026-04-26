"""SciTeX sh — thin compatibility shim for scitex-sh.

Aliases ``scitex.sh`` to the standalone ``scitex_sh`` package via ``sys.modules``.
``scitex.sh is scitex_sh``.

Install: ``pip install scitex[sh]``  (or ``pip install scitex-sh``).
See: https://github.com/ywatanabe1989/scitex-sh
"""

import sys as _sys

try:
    import scitex_sh as _real
except ImportError as _e:  # pragma: no cover
    raise ImportError(
        "scitex.sh requires the 'scitex-sh' package. "
        "Install with: pip install scitex[sh]  (or: pip install scitex-sh)"
    ) from _e

_sys.modules[__name__] = _real
