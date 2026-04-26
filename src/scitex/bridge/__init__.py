"""SciTeX bridge — thin compatibility shim for scitex-bridge.

Aliases ``scitex.bridge`` to the standalone ``scitex_bridge`` package via
``sys.modules``. ``scitex.bridge is scitex_bridge``.

Install: ``pip install scitex[bridge]``  (or ``pip install scitex-bridge``).
See: https://github.com/ywatanabe1989/scitex-bridge
"""

import sys as _sys

try:
    import scitex_bridge as _real
except ImportError as _e:  # pragma: no cover
    raise ImportError(
        "scitex.bridge requires the 'scitex-bridge' package. "
        "Install with: pip install scitex[bridge]  (or: pip install scitex-bridge)"
    ) from _e

_sys.modules[__name__] = _real
