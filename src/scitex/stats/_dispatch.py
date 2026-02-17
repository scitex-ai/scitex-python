#!/usr/bin/env python3
# Timestamp: "2026-02-17"
# File: scitex/stats/_dispatch.py
"""Unified statistical test dispatcher.

Provides ``run_test()`` — a single entry-point that routes a test name
to the corresponding ``stx.stats.test_*()`` function, normalises the
result for JSON serialisation, and optionally captures a plot.
"""

from __future__ import annotations

import os
from typing import Any, Dict, List, Literal, Optional, Union

import numpy as np

__FILE__ = __file__
__DIR__ = os.path.dirname(__FILE__)

# ---------------------------------------------------------------------------
# Test categories — determines how arguments are routed
# ---------------------------------------------------------------------------

# Tests that accept (x, y, alternative=...)
_TWO_SAMPLE = {
    "ttest",
    "ttest_ind",
    "brunnermunzel",
    "brunner_munzel",
    "mannwhitneyu",
    "mann_whitney",
    "ks_2samp",
    "pearson",
    "spearman",
    "kendall",
}

# Tests that accept (x, y) without alternative
_PAIRED = {"ttest_rel", "ttest_paired", "wilcoxon"}

# Tests that accept (data,) only
_ONE_SAMPLE = {"shapiro", "ks_1samp"}

# Tests that accept (data, popmean=...)
_ONE_SAMPLE_MEAN = {"ttest_1samp"}

# Tests that accept (groups,)
_GROUP = {"anova", "kruskal"}

# Tests that accept np.column_stack(groups) as first positional
_STACKED_GROUP = {"friedman"}

# Contingency-table tests
_CONTINGENCY = {"chi2", "fisher"}

# Canonical name mapping — aliases to the function name in stx.stats
_ALIASES = {
    "ttest": "test_ttest_ind",
    "ttest_ind": "test_ttest_ind",
    "ttest_rel": "test_ttest_rel",
    "ttest_paired": "test_ttest_rel",
    "ttest_1samp": "test_ttest_1samp",
    "anova": "test_anova",
    "brunnermunzel": "test_brunner_munzel",
    "brunner_munzel": "test_brunner_munzel",
    "mannwhitneyu": "test_mannwhitneyu",
    "mann_whitney": "test_mannwhitneyu",
    "wilcoxon": "test_wilcoxon",
    "kruskal": "test_kruskal",
    "friedman": "test_friedman",
    "chi2": "test_chi2",
    "fisher": "test_fisher",
    "shapiro": "test_shapiro",
    "ks_1samp": "test_ks_1samp",
    "ks_2samp": "test_ks_2samp",
    "pearson": "test_pearson",
    "spearman": "test_spearman",
    "kendall": "test_kendall",
}


def available_tests() -> List[str]:
    """Return sorted list of canonical test names accepted by ``run_test``.

    Returns
    -------
    list of str
        Accepted test name strings (including aliases).
    """
    return sorted(_ALIASES.keys())


def run_test(
    test_name: str,
    data: Optional[Union[np.ndarray, list]] = None,
    data2: Optional[Union[np.ndarray, list]] = None,
    groups: Optional[List[Union[np.ndarray, list]]] = None,
    alternative: Literal["two-sided", "greater", "less"] = "two-sided",
    plot: bool = False,
    popmean: float = 0,
    return_as: str = "dict",
    json_safe: bool = True,
    **kwargs: Any,
) -> Dict[str, Any]:
    """Run a statistical test by name and return a normalised result dict.

    Parameters
    ----------
    test_name : str
        Name of the test (e.g. ``"ttest_ind"``, ``"anova"``).
        See :func:`available_tests` for the full list including aliases.
    data : array-like, optional
        Primary data array.
    data2 : array-like, optional
        Second data array (for two-sample / paired tests).
    groups : list of array-like, optional
        List of group arrays (for ANOVA, Kruskal, etc.).
    alternative : str, default ``"two-sided"``
        Alternative hypothesis for applicable tests.
    plot : bool, default ``False``
        Whether to generate a plot.
    popmean : float, default ``0``
        Population mean for one-sample t-test.
    return_as : str, default ``"dict"``
        Passed through to the underlying test function.
    json_safe : bool, default ``True``
        If True, apply :func:`to_json_safe` to the result.
    **kwargs
        Additional keyword arguments forwarded to the test function.

    Returns
    -------
    dict
        Test result dictionary. When *json_safe* is True, all numpy
        scalars are converted to Python types and a ``formatted`` key
        is added.

    Raises
    ------
    ValueError
        If *test_name* is not recognised.
    """
    import scitex.stats as stats

    if test_name not in _ALIASES:
        raise ValueError(
            f"Unknown test: {test_name}. "
            f"Available: {', '.join(sorted(_ALIASES.keys()))}"
        )

    func_name = _ALIASES[test_name]
    func = getattr(stats, func_name)

    # Route arguments based on test category
    result = _call_test(
        func,
        test_name,
        data=data,
        data2=data2,
        groups=groups,
        alternative=alternative,
        plot=plot,
        popmean=popmean,
        return_as=return_as,
        **kwargs,
    )

    # Some test functions return (result, fig) tuples
    if isinstance(result, tuple):
        result = result[0]

    if json_safe:
        from scitex.stats._utils._serialize import to_json_safe

        result = to_json_safe(result)

    return result


def _call_test(
    func,
    test_name: str,
    *,
    data,
    data2,
    groups,
    alternative,
    plot,
    popmean,
    return_as,
    **kwargs,
):
    """Dispatch to the correct test function with proper arguments."""
    common = {"plot": plot, "return_as": return_as}
    common.update(kwargs)

    if test_name in _TWO_SAMPLE:
        return func(data, data2, alternative=alternative, **common)

    if test_name in _PAIRED:
        return func(data, data2, **common)

    if test_name in _ONE_SAMPLE:
        return func(data, **common)

    if test_name in _ONE_SAMPLE_MEAN:
        return func(data, popmean=popmean, **common)

    if test_name in _GROUP:
        return func(groups, **common)

    if test_name in _STACKED_GROUP:
        return func(np.column_stack(groups), **common)

    if test_name in _CONTINGENCY:
        if groups is not None:
            table = np.array(groups, dtype=float)
        else:
            table = np.vstack([data, data2])
        return func(table, **common)

    raise ValueError(f"No dispatch rule for test: {test_name}")


__all__ = ["run_test", "available_tests"]

# EOF
