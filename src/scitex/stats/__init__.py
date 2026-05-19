#!/usr/bin/env python3
# Timestamp: 2026-03-11
# File: src/scitex/stats/__init__.py
"""SciTeX Stats — thin re-export from standalone scitex-stats package.

All core implementations live in the ``scitex-stats`` package.
This module re-exports the public API and adds scitex-specific
integration (bundle interop, figrecipe annotations).
"""

# =============================================================================
# Core re-export from standalone scitex-stats
# =============================================================================

# Check if torch is available for GPU acceleration (internal flag)
from scitex_dev import try_import_optional
from scitex_stats import *  # noqa: F401,F403

# Explicit re-exports for IDE support and backward compatibility
from scitex_stats import (  # noqa: F401
    StatContext,
    StatStyle,
    TestRule,
    _utils,
    auto,
    available_tests,
    check_applicable,
    correct,
    describe,
    descriptive,
    effect_sizes,
    get_stat_style,
    p_to_stars,
    posthoc,
    power,
    recommend_tests,
    run_test,
    test_anova,
    test_anova_2way,
    test_anova_rm,
    test_brunner_munzel,
    test_chi2,
    test_cochran_q,
    test_fisher,
    test_friedman,
    test_kendall,
    test_kruskal,
    test_ks_1samp,
    test_ks_2samp,
    test_mannwhitneyu,
    test_mcnemar,
    test_normality,
    test_pearson,
    test_shapiro,
    test_spearman,
    test_theilsen,
    test_ttest_1samp,
    test_ttest_ind,
    test_ttest_rel,
    test_wilcoxon,
    tests,
    to_json_safe,
)

# Private re-exports used by internal code
from scitex_stats.auto import TEST_RULES as _TEST_RULES  # noqa: F401
from scitex_stats.auto import format_test_line as _format_test_line  # noqa: F401
from scitex_stats.auto import get_menu_items as _get_menu_items  # noqa: F401

# Check if torch is available for GPU acceleration (internal flag)
_torch = try_import_optional("torch", extra="nn", pkg="scitex")
_TORCH_AVAILABLE = _torch is not None
del _torch

# =============================================================================
# SciTeX-specific integration (bundle, figrecipe)
# =============================================================================

from ._integration import (  # noqa: F401,E402
    BUNDLE_AVAILABLE,
    Stats,
    annotate,
    load_and_annotate,
    load_stats,
    save_stats,
    test_result_to_stats,
    to_figrecipe,
)

__all__ = [
    # Submodules
    "auto",
    "correct",
    "descriptive",
    "effect_sizes",
    "power",
    "posthoc",
    "tests",
    # Descriptive
    "describe",
    # Dispatcher
    "run_test",
    "available_tests",
    # JSON serialization
    "to_json_safe",
    # Parametric (6)
    "test_ttest_ind",
    "test_ttest_rel",
    "test_ttest_1samp",
    "test_anova",
    "test_anova_rm",
    "test_anova_2way",
    # Nonparametric (5)
    "test_brunner_munzel",
    "test_wilcoxon",
    "test_kruskal",
    "test_mannwhitneyu",
    "test_friedman",
    # Correlation (4)
    "test_pearson",
    "test_spearman",
    "test_kendall",
    "test_theilsen",
    # Categorical (4)
    "test_chi2",
    "test_fisher",
    "test_mcnemar",
    "test_cochran_q",
    # Normality (4)
    "test_shapiro",
    "test_normality",
    "test_ks_1samp",
    "test_ks_2samp",
    # Auto convenience
    "StatContext",
    "TestRule",
    "StatStyle",
    "check_applicable",
    "recommend_tests",
    "get_stat_style",
    "p_to_stars",
    # SciTeX integration
    "Stats",
    "test_result_to_stats",
    "save_stats",
    "load_stats",
    "to_figrecipe",
    "annotate",
    "load_and_annotate",
]

# Register scitex_stats submodules at the `scitex.stats.<name>` import path.
# Without this, `from scitex.stats._utils import X` fails: Python's import
# machinery resolves dotted-paths against sys.modules + finder hooks, not
# the parent's namespace dict (where the `from scitex_stats import _utils`
# above has only added it as an attribute). Mirroring the alias-shim pattern
# from `scitex.plt = figrecipe`.
import sys as _sys

import scitex_stats as _scitex_stats

for _submod in ("_utils",):
    _mod = getattr(_scitex_stats, _submod, None)
    if _mod is not None:
        _sys.modules[f"scitex.stats.{_submod}"] = _mod

del _sys, _scitex_stats

# EOF
