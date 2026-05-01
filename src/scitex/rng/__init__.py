"""DEPRECATED: ``scitex.rng`` was merged into ``scitex.repro``.

This compatibility shim emits a DeprecationWarning and re-exports the
random-state primitives from ``scitex.repro``. Both ``import scitex.rng``
and ``from scitex.rng import RandomStateManager`` keep working until the
next major release.
"""

import warnings

warnings.warn(
    "scitex.rng is deprecated, use scitex.repro instead.",
    DeprecationWarning,
    stacklevel=2,
)

from scitex.repro import RandomStateManager, get, reset  # noqa: F401

__all__ = ["RandomStateManager", "get", "reset"]
