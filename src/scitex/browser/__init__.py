"""SciTeX browser — thin compatibility shim for scitex-browser.

Aliases ``scitex.browser`` to the standalone ``scitex_browser`` package via
``sys.modules`` so ``scitex.browser is scitex_browser`` and any new public name
added to scitex_browser is automatically visible.

Install: ``pip install scitex-browser``.
See: https://github.com/ywatanabe1989/scitex-browser
"""

import sys as _sys

try:
    import scitex_browser as _real
except ImportError as _e:  # pragma: no cover
    raise ImportError(
        "scitex.browser requires the 'scitex-browser' package. "
        "Install with: pip install scitex-browser"
    ) from _e

_sys.modules[__name__] = _real
