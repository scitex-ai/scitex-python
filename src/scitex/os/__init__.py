"""SciTeX os — thin compatibility shim for scitex-os.

Aliases ``scitex.os`` to the standalone ``scitex_os`` package via ``sys.modules``.
``scitex.os is scitex_os``.

Install: ``pip install scitex[os]``  (or ``pip install scitex-os``).
See: https://github.com/ywatanabe1989/scitex-os
"""

import sys as _sys

try:
    import scitex_os as _real
except ImportError as _e:  # pragma: no cover
    raise ImportError(
        "scitex.os requires the 'scitex-os' package. "
        "Install with: pip install scitex[os]  (or: pip install scitex-os)"
    ) from _e

_sys.modules[__name__] = _real
