"""SciTeX session — thin compatibility shim for scitex-session.

Aliases ``scitex.session`` to the standalone ``scitex_session`` package via
``sys.modules``. ``scitex.session is scitex_session``.

Install: ``pip install scitex[session]``  (or ``pip install scitex-session``).
See: https://github.com/ywatanabe1989/scitex-session
"""

import sys as _sys

try:
    import scitex_session as _real
except ImportError as _e:  # pragma: no cover
    raise ImportError(
        "scitex.session requires the 'scitex-session' package. "
        "Install with: pip install scitex[session]  (or: pip install scitex-session)"
    ) from _e

_sys.modules[__name__] = _real
