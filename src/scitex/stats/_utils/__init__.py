#!/usr/bin/env python3
# File: ./scitex_repo/src/scitex/stats/utils/__init__.py

"""
Statistical utilities.

Helper functions for effect sizes, power analysis, formatting, and data normalization.
"""

# Effect sizes
# CSV/DataFrame column resolution
from ._csv_support import resolve_columns, resolve_groups
from ._effect_size import (
    cliffs_delta,
    cohens_d,
    epsilon_squared,
    eta_squared,
    interpret_cliffs_delta,
    interpret_cohens_d,
    interpret_epsilon_squared,
    interpret_eta_squared,
    interpret_prob_superiority,
    prob_superiority,
)

# Formatters
from ._formatters import fmt_stat, fmt_sym, italicize_stats, p2stars

# Normalizers
from ._normalizers import force_dataframe

# Power analysis
from ._power import power_ttest, sample_size_ttest

# Serialization
from ._serialize import to_json_safe

__all__ = [
    # Effect sizes
    "cohens_d",
    "cliffs_delta",
    "prob_superiority",
    "eta_squared",
    "epsilon_squared",
    "interpret_cohens_d",
    "interpret_cliffs_delta",
    "interpret_prob_superiority",
    "interpret_eta_squared",
    "interpret_epsilon_squared",
    # Power analysis
    "power_ttest",
    "sample_size_ttest",
    # Formatters
    "fmt_stat",
    "fmt_sym",
    "italicize_stats",
    "p2stars",
    # Normalizers
    "force_dataframe",
    # Serialization
    "to_json_safe",
    # CSV/DataFrame column resolution
    "resolve_columns",
    "resolve_groups",
]
