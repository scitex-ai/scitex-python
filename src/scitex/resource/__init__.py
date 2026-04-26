"""SciTeX resource — thin compatibility shim for scitex-resource.

Aliases ``scitex.resource`` to the standalone ``scitex_resource`` package via
``sys.modules``. ``scitex.resource is scitex_resource``.

Install: ``pip install scitex[resource]``  (or ``pip install scitex-resource``).
See: https://github.com/ywatanabe1989/scitex-resource
"""

import sys as _sys

try:
    import scitex_resource as _real
except ImportError as _e:  # pragma: no cover
    raise ImportError(
        "scitex.resource requires the 'scitex-resource' package. "
        "Install with: pip install scitex[resource]  (or: pip install scitex-resource)"
    ) from _e

_sys.modules[__name__] = _real
