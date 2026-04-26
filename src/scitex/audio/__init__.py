"""SciTeX audio — thin compatibility shim for scitex-audio.

Aliases ``scitex.audio`` to the standalone ``scitex_audio`` package via
``sys.modules`` so ``scitex.audio is scitex_audio`` and any new public name
added to scitex_audio is automatically visible.

Install: ``pip install scitex-audio``.
See: https://github.com/ywatanabe1989/scitex-audio
"""

import sys as _sys

try:
    import scitex_audio as _real
except ImportError as _e:  # pragma: no cover
    raise ImportError(
        "scitex.audio requires the 'scitex-audio' package. "
        "Install with: pip install scitex-audio"
    ) from _e

_sys.modules[__name__] = _real
