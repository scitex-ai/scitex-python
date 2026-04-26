"""SciTeX audit — thin compatibility shim for scitex-audit.

Aliases ``scitex.audit`` to the standalone ``scitex_audit`` package via
``sys.modules`` so ``scitex.audit is scitex_audit`` and any new public name
added to scitex_audit is automatically visible.

Install: ``pip install scitex-audit``.
See: https://github.com/ywatanabe1989/scitex-audit
"""

import sys as _sys

try:
    import scitex_audit as _real
except ImportError as _e:  # pragma: no cover
    raise ImportError(
        "scitex.audit requires the 'scitex-audit' package. "
        "Install with: pip install scitex-audit"
    ) from _e

_sys.modules[__name__] = _real
