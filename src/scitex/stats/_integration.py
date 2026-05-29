#!/usr/bin/env python3
"""Thin re-export of stats integration glue.

Per SOC.md R5/C4, the integration code now lives in the standalone
packages:

- Bundle wiring (``Stats`` schema + ``save_stats`` / ``load_stats`` /
  ``test_result_to_stats``) lives in
  ``scitex_io.bundle.kinds._stats._integration`` because the bundle
  dispatcher is scitex-io's domain (Q2 / Task 8).
- Figrecipe annotation glue (``to_figrecipe`` / ``annotate`` /
  ``load_and_annotate``) lives in
  ``scitex_stats._figrecipe_integration`` because the natural call
  site is stats-led (Q1 / Task 10).

This umbrella file exists only so that legacy callers writing
``from scitex.stats._integration import ...`` keep working.
"""

from __future__ import annotations

# Bundle-side integration
from scitex_io.bundle.kinds._stats._integration import (  # noqa: F401
    BUNDLE_AVAILABLE,
    load_stats,
    save_stats,
    test_result_to_stats,
)

# Figrecipe-side integration
from scitex_stats._figrecipe_integration import (  # noqa: F401
    annotate,
    load_and_annotate,
    to_figrecipe,
)

# Stats dataclass — preferred public path is ``from scitex_io.bundle
# import Stats`` (the bundle subsystem owns the schema). Keep the
# umbrella re-export so ``from scitex.stats._integration import Stats``
# still resolves.
try:
    from scitex_io.bundle import Stats  # type: ignore[attr-defined]
except ImportError:
    Stats = None  # type: ignore[assignment]


__all__ = [
    "Stats",
    "BUNDLE_AVAILABLE",
    "test_result_to_stats",
    "save_stats",
    "load_stats",
    "to_figrecipe",
    "annotate",
    "load_and_annotate",
]
