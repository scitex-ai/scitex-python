"""SciTeX decorators — thin compatibility shim for scitex-decorators.

Aliases ``scitex.decorators`` to the standalone ``scitex_decorators`` package
via ``sys.modules``. ``scitex.decorators is scitex_decorators``.

The full type-conversion / caching / batching / deprecation decorator surface
is preserved.

Install: ``pip install scitex[decorators]``  (or ``pip install scitex-decorators``).
See: https://github.com/ywatanabe1989/scitex-decorators
"""

import sys as _sys

try:
    import scitex_decorators as _real
except ImportError as _e:  # pragma: no cover
    raise ImportError(
        "scitex.decorators requires the 'scitex-decorators' package. "
        "Install with: pip install scitex[decorators]  (or: pip install scitex-decorators)"
    ) from _e

_sys.modules[__name__] = _real
