#!/usr/bin/env python3
"""Re-export shim — implementation moved to ``scitex_stats._dataclasses``.

Each scitex ecosystem package owns its domain dataclasses; the stats
schemas (``Stats``, ``EffectSize``, GUI positioning/styling, …) now
live in ``scitex_stats._dataclasses._Stats``. This module preserves the
historical ``scitex.io.bundle.kinds._stats._dataclasses._Stats`` import
path used by the umbrella's bundle dispatcher and Bundle/loader/saver
classes.

Bundle-format identity (STATS_VERSION + the dataclasses' field shape)
is the contract; keeping a single source of truth in scitex_stats
prevents the umbrella and the standalone from drifting out of sync.
"""

from scitex_stats._dataclasses._Stats import *  # noqa: F401, F403
from scitex_stats._dataclasses._Stats import (  # noqa: F401  (explicit for clarity)
    STATS_VERSION,
    Analysis,
    DataRef,
    EffectSize,
    Position,
    PositionMode,
    StatDisplay,
    StatMethod,
    StatPositioning,
    StatResult,
    Stats,
    StatStyling,
    SymbolStyle,
    UnitType,
)
