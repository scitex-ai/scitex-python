"""SciTeX introspect — thin compatibility shim for scitex-introspect.

Aliases ``scitex.introspect`` to the standalone ``scitex_introspect`` package
via ``sys.modules``. ``scitex.introspect is scitex_introspect``.

Install: ``pip install scitex[introspect]``  (or ``pip install scitex-introspect``).
See: https://github.com/ywatanabe1989/scitex-introspect
"""

import sys as _sys

try:
    import scitex_introspect as _real
except ImportError as _e:  # pragma: no cover
    raise ImportError(
        "scitex.introspect requires the 'scitex-introspect' package. "
        "Install with: pip install scitex[introspect]  (or: pip install scitex-introspect)"
    ) from _e

_sys.modules[__name__] = _real
