"""SciTeX gists — thin compatibility shim for scitex-gists.

Aliases ``scitex.gists`` to the standalone ``scitex_gists`` package via
``sys.modules`` so ``scitex.gists is scitex_gists`` and any new public name
added to scitex_gists is automatically visible.

Install: ``pip install scitex-gists``.
See: https://github.com/ywatanabe1989/scitex-gists
"""

import sys as _sys

try:
    import scitex_gists as _real
except ImportError as _e:  # pragma: no cover
    raise ImportError(
        "scitex.gists requires the 'scitex-gists' package. "
        "Install with: pip install scitex-gists"
    ) from _e

_sys.modules[__name__] = _real
