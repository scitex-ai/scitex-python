"""SciTeX config — thin compatibility shim for scitex-config.

Aliases ``scitex.config`` to the standalone ``scitex_config`` package via
``sys.modules``. ``scitex.config is scitex_config``.

Install: ``pip install scitex[config]``  (or ``pip install scitex-config``).
See: https://github.com/ywatanabe1989/scitex-config
"""

import sys as _sys

try:
    import scitex_config as _real
except ImportError as _e:  # pragma: no cover
    raise ImportError(
        "scitex.config requires the 'scitex-config' package. "
        "Install with: pip install scitex[config]  (or: pip install scitex-config)"
    ) from _e

_sys.modules[__name__] = _real
