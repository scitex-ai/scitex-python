#!/usr/bin/env python3
"""SciTeX Stats Module - Professional Statistical Testing Framework.

Clean, normalized API for statistical analysis with publication-ready outputs.

Organized submodules:
- auto: Automatic test selection, recommendation, and journal-style formatting
- correct: Multiple comparison correction methods (Bonferroni, FDR, Holm, Sidak)
- effect_sizes: Effect size computations and interpretations
- power: Statistical power analysis
- posthoc: Post-hoc tests (Tukey, Dunnett, Games-Howell)
- tests: Statistical tests (correlation, etc.)
- descriptive: Descriptive statistics

Quick Start (Auto Selection):
----------------------------
>>> from scitex.stats.auto import StatContext, recommend_tests
>>> ctx = StatContext(
...     n_groups=2,
...     sample_sizes=[30, 32],
...     outcome_type="continuous",
...     design="between",
...     paired=False,
...     has_control_group=False,
...     n_factors=1
... )
>>> tests = recommend_tests(ctx, top_k=3)
>>> print(tests)  # ['brunner_munzel', 'ttest_ind', 'mannwhitneyu']
"""

# Import organized submodules (public)
# Internal submodule (hidden with underscore prefix)
from . import (  # noqa: F401
    _utils,
    auto,
    correct,
    descriptive,
    effect_sizes,
    posthoc,
    power,
    tests,
)

# Unified test dispatcher
from ._dispatch import available_tests, run_test

# JSON-safe serialization
from ._utils._serialize import to_json_safe

# Convenience re-export from descriptive
from .descriptive import describe

# Re-export all 23 test functions at stx.stats level
from .tests import (  # noqa: F401; Nonparametric (5); Categorical (4); Correlation (4); Normality (4); Parametric (6)
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
)

# Check if torch is available for GPU acceleration (internal flag)
try:
    import torch  # noqa: F401

    _TORCH_AVAILABLE = True
except ImportError:
    _TORCH_AVAILABLE = False

# Export key auto module classes at top level for convenience
# Internal imports (hidden with underscore prefix)
from .auto import TEST_RULES as _TEST_RULES  # noqa: F401
from .auto import (
    StatContext,
    StatStyle,
    TestRule,
    check_applicable,
    get_stat_style,
    p_to_stars,
    recommend_tests,
)
from .auto import format_test_line as _format_test_line  # noqa: F401
from .auto import get_menu_items as _get_menu_items  # noqa: F401

# =============================================================================
# Stats Schema - Use scitex.io.bundle.Stats as single source of truth
# =============================================================================

# Re-export Stats from bundle module
try:
    from scitex.io.bundle import Stats  # type: ignore[attr-defined]

    BUNDLE_AVAILABLE = True
except ImportError:
    Stats = None
    BUNDLE_AVAILABLE = False


def test_result_to_stats(result: dict) -> "Stats":
    """Convert test result dict to Stats schema.

    Parameters
    ----------
    result : dict
        Test result dictionary. Supports both formats:

        Legacy flat format (from examples):
        - name: "Control vs Treatment"
        - method: "t-test"  # string
        - p_value: 0.003
        - effect_size: 1.21
        - ci95: [0.5, 1.8]

        New nested format (from test functions):
        - method: {"name": "t-test", "variant": "independent"}
        - results: {"statistic": 2.5, "statistic_name": "t", "p_value": 0.01}

    Returns
    -------
    Stats
        Stats object suitable for bundle storage

    Example
    -------
    >>> result = stats.t_test(x, y)
    >>> stat_obj = stats.test_result_to_stats(result)
    >>> bundle.stats = stat_obj
    """
    if not BUNDLE_AVAILABLE:
        raise ImportError("scitex.io.bundle is required for Stats conversion")

    import uuid

    from scitex.io.bundle._stats._dataclasses._Stats import (
        Analysis,
        EffectSize,
        StatMethod,
        StatResult,
    )

    # Handle legacy flat format vs new nested format
    method_data = result.get("method", {})
    if isinstance(method_data, str):
        # Legacy format: method is a string
        method = StatMethod(
            name=method_data,
            variant=None,
            parameters={},
        )
        # Legacy format has flat p_value, effect_size
        effect_size = None
        es_val = result.get("effect_size")
        if es_val is not None:
            ci = result.get("ci95", [])
            effect_size = EffectSize(
                name="d",
                value=float(es_val),
                ci_lower=ci[0] if len(ci) > 0 else None,
                ci_upper=ci[1] if len(ci) > 1 else None,
            )
        stat_result = StatResult(
            statistic=result.get("statistic", 0.0),
            statistic_name=result.get("statistic_name", ""),
            p_value=result.get("p_value", 1.0),
            df=result.get("df"),
            effect_size=effect_size,
            significant=result.get("p_value", 1.0) < 0.05,
            alpha=0.05,
        )
        analysis_name = result.get("name", "comparison")
    else:
        # New nested format
        method = StatMethod(
            name=method_data.get("name", "unknown"),
            variant=method_data.get("variant"),
            parameters=method_data.get("parameters", {}),
        )

        # Build result
        results_data = result.get("results", {})
        effect_size = None
        if "effect_size" in results_data:
            es = results_data["effect_size"]
            effect_size = EffectSize(
                name=es.get("name", ""),
                value=es.get("value", 0.0),
                ci_lower=es.get("ci_lower"),
                ci_upper=es.get("ci_upper"),
            )

        stat_result = StatResult(
            statistic=results_data.get("statistic", 0.0),
            statistic_name=results_data.get("statistic_name", ""),
            p_value=results_data.get("p_value", 1.0),
            df=results_data.get("df"),
            effect_size=effect_size,
            significant=results_data.get("significant"),
            alpha=results_data.get("alpha", 0.05),
        )
        analysis_name = result.get("name", "analysis")

    # Build analysis (name stored in inputs for reference)
    inputs = result.get("inputs", {})
    inputs["comparison_name"] = analysis_name
    analysis = Analysis(
        result_id=str(uuid.uuid4()),
        method=method,
        results=stat_result,
        inputs=inputs,
    )

    return Stats(analyses=[analysis])


# =============================================================================
# Figrecipe Integration (for plot annotations)
# =============================================================================

from ._figrecipe_integration import (  # noqa: E402
    annotate,
    load_and_annotate,
    to_figrecipe,
)

# =============================================================================
# .stats Bundle Support
# =============================================================================


def save_stats(
    comparisons,
    path,
    metadata=None,
    as_zip=False,
):
    """
    Save statistical results as a SciTeX bundle.

    Parameters
    ----------
    comparisons : list of dict
        List of comparison results.
    path : str or Path
        Output path (e.g., "results.stats" or "results.stats.zip").
    metadata : dict, optional
        Additional metadata.
    as_zip : bool, optional
        If True, save as ZIP archive (default: False).

    Returns
    -------
    Path
        Path to saved bundle.
    """
    from pathlib import Path

    from scitex.io.bundle import Bundle

    p = Path(path)
    if as_zip and not p.suffix == ".zip":
        p = p.with_suffix(".zip")

    # Create bundle
    bundle = Bundle(p, create=True, bundle_type="stats")  # type: ignore[call-arg]

    # Convert comparisons to Stats
    if comparisons:
        if isinstance(comparisons[0], dict):
            # Convert list of dicts to Stats
            stats = Stats(analyses=[])
            for comp in comparisons:
                analysis_stats = test_result_to_stats(comp)
                stats.analyses.extend(analysis_stats.analyses)
            bundle.stats = stats
        else:
            # Already Stats objects
            bundle.stats = comparisons

    bundle.save()
    return p


def load_stats(path):
    """
    Load a stats bundle.

    Parameters
    ----------
    path : str or Path
        Path to bundle (.stats or .stats.zip).

    Returns
    -------
    dict
        Stats data with 'comparisons' and 'metadata'.
        Each comparison is a flat dict with:
        - name, method, p_value, effect_size, ci95, formatted
    """
    from scitex.io.bundle import Bundle

    bundle = Bundle(path)

    comparisons = []
    if bundle.stats and bundle.stats.analyses:
        for analysis in bundle.stats.analyses:
            # Convert back to flat format for compatibility
            ad = analysis.to_dict()
            p_val = ad.get("results", {}).get("p_value", 1.0)
            es_data = ad.get("results", {}).get("effect_size", {})
            es_val = es_data.get("value", 0.0) if es_data else 0.0
            ci = [es_data.get("ci_lower"), es_data.get("ci_upper")] if es_data else []
            ci = [v for v in ci if v is not None]

            # Format p-value as stars
            if p_val < 0.001:
                formatted = "***"
            elif p_val < 0.01:
                formatted = "**"
            elif p_val < 0.05:
                formatted = "*"
            else:
                formatted = "ns"

            flat = {
                "name": ad.get("inputs", {}).get("comparison_name", "comparison"),
                "method": ad.get("method", {}).get("name", "unknown"),
                "p_value": p_val,
                "effect_size": es_val,
                "ci95": ci,
                "formatted": formatted,
            }
            comparisons.append(flat)

    return {
        "comparisons": comparisons,
        "metadata": bundle.node.to_dict() if bundle.node else {},  # type: ignore[attr-defined]
    }


__all__ = [
    # Main submodules (public)
    "auto",
    "correct",
    "descriptive",
    "effect_sizes",
    "power",
    "posthoc",
    "tests",
    # Descriptive convenience export
    "describe",
    # Unified test dispatcher
    "run_test",
    "available_tests",
    # JSON-safe serialization
    "to_json_safe",
    # Statistical tests - public API (23 tests)
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
    # Stats schema
    "Stats",
    # Auto module convenience exports
    "StatContext",
    "TestRule",
    "StatStyle",
    "check_applicable",
    "recommend_tests",
    "get_stat_style",
    "p_to_stars",
    # Conversion utilities
    "test_result_to_stats",
    # Bundle functions
    "save_stats",
    "load_stats",
    # Figrecipe integration
    "to_figrecipe",
    "annotate",
    "load_and_annotate",
]
