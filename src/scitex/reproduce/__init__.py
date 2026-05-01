"""DEPRECATED: ``scitex.reproduce`` was renamed to ``scitex.repro``.

This compatibility shim emits a DeprecationWarning and re-exports
everything from ``scitex.repro``. Both ``import scitex.reproduce`` and
``from scitex.reproduce import X`` keep working until the next major
release.
"""

import warnings

warnings.warn(
    "scitex.reproduce is deprecated, use scitex.repro instead.",
    DeprecationWarning,
    stacklevel=2,
)

from scitex.repro import *  # noqa: F401,F403
