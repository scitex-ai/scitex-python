"""SciTeX web — thin compatibility shim for scitex-web.

Aliases ``scitex.web`` to the standalone ``scitex_web`` package via ``sys.modules``.
``scitex.web is scitex_web``.

Install: ``pip install scitex[web]``  (or ``pip install scitex-web``).
See: https://github.com/ywatanabe1989/scitex-web
"""

import sys as _sys

try:
    import scitex_web as _real
except ImportError as _e:  # pragma: no cover
    raise ImportError(
        "scitex.web requires the 'scitex-web' package. "
        "Install with: pip install scitex[web]  (or: pip install scitex-web)"
    ) from _e

_sys.modules[__name__] = _real
