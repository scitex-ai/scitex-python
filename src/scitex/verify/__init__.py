"""DEPRECATED: ``scitex.verify`` was renamed to ``scitex.clew``.

This compatibility shim emits a DeprecationWarning and re-exports
everything from ``scitex.clew``. ``import scitex.verify`` and
``from scitex.verify import X`` both keep working until the next major
release.
"""

import warnings

warnings.warn(
    "scitex.verify is deprecated, use scitex.clew instead.",
    DeprecationWarning,
    stacklevel=2,
)

from scitex.clew import *  # noqa: F401,F403
