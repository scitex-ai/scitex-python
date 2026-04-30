"""DEPRECATED: ``scitex.ml`` was renamed to ``scitex.ai``.

This compatibility shim emits a DeprecationWarning and re-exports
everything from ``scitex.ai``. ``import scitex.ml`` and
``from scitex.ml import X`` both keep working until the next major release.
"""

import warnings

warnings.warn(
    "scitex.ml is deprecated, use scitex.ai instead.",
    DeprecationWarning,
    stacklevel=2,
)

from scitex.ai import *  # noqa: F401,F403
