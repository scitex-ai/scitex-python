"""SciTeX container — thin compatibility shim for scitex-container.

Aliases ``scitex.container`` to the standalone ``scitex_container`` package via
``sys.modules`` so ``scitex.container is scitex_container`` and every
sub-namespace (``scitex.container.apptainer``, ``.docker``, ``.host``,
``.env_snapshot``) keeps resolving.

Install: ``pip install scitex[container]``  (or ``pip install scitex-container``).
See: https://github.com/ywatanabe1989/scitex-container
"""

import sys as _sys

try:
    import scitex_container as _real
except ImportError as _e:  # pragma: no cover
    raise ImportError(
        "scitex.container requires the 'scitex-container' package. "
        "Install with: pip install scitex[container]  (or: pip install scitex-container)"
    ) from _e

_sys.modules[__name__] = _real
