#!/usr/bin/env python3
# Timestamp: 2025-12-21
# File: /home/ywatanabe/proj/scitex-code/src/scitex/fts/_kinds/_stats/__init__.py

"""Stats kind - Statistical analysis results.

A stats bundle contains statistical test results (payload/stats.json).
Used for annotations like p-values, effect sizes, confidence intervals.

Structure:
- payload/stats.json: Statistical results
- analyses: List of statistical tests and their results
"""

# Public dataclasses: scitex_stats owns the schema (single source of truth).
from scitex_stats._dataclasses import (  # noqa: F401
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

__all__ = [
    "STATS_VERSION",
    "Stats",
    # Type aliases
    "PositionMode",
    "UnitType",
    "SymbolStyle",
    # GUI classes
    "Position",
    "StatStyling",
    "StatPositioning",
    # Core classes
    "DataRef",
    "EffectSize",
    "StatMethod",
    "StatResult",
    "StatDisplay",
    "Analysis",
]

# EOF
