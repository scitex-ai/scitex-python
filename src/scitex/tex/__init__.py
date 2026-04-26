"""SciTeX tex — thin compatibility shim for scitex-tex.

Aliases ``scitex.tex`` to the standalone ``scitex_tex`` package via ``sys.modules``.
``scitex.tex is scitex_tex``.

Install: ``pip install scitex[tex]``  (or ``pip install scitex-tex``).
See: https://github.com/ywatanabe1989/scitex-tex
"""

import sys as _sys

try:
    import scitex_tex as _real
except ImportError as _e:  # pragma: no cover
    raise ImportError(
        "scitex.tex requires the 'scitex-tex' package. "
        "Install with: pip install scitex[tex]  (or: pip install scitex-tex)"
    ) from _e

_sys.modules[__name__] = _real
