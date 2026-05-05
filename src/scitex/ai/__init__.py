#!/usr/bin/env python3
# File: src/scitex/ai/__init__.py
# ----------------------------------------
"""SciTeX AI — thin compatibility shim for the standalone ``scitex-ai`` package.

Implementation, tests, and version live in ``scitex-ai`` (PyPI:
``scitex-ai``, import: ``scitex_ai``). This shim makes ``scitex.ai.X`` and
``scitex_ai.X`` resolve to the same object, including deep submodule paths
(``scitex.ai.classification.timeseries.…`` etc.) via ``sys.modules``
aliasing.

If the standalone is not installed, importing this module raises a clear
``ImportError`` pointing the user at ``pip install scitex[ai]``.

See ``_skills/general/01_ecosystem_05_re-export.md`` for the full re-export
convention.
"""

from __future__ import annotations

import sys as _sys

try:
    import scitex_ai as _real
except ImportError as _e:  # pragma: no cover — explicit user-facing error
    raise ImportError(
        "scitex.ai requires the 'scitex-ai' package. "
        "Install with: pip install scitex[ai]"
    ) from _e

# Module-level sys.modules aliasing — preserves deep submodule paths
# (e.g. scitex.ai.classification.timeseries._TimeSeriesStratifiedSplit).
_sys.modules[__name__] = _real
