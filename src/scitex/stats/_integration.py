#!/usr/bin/env python3
# Timestamp: 2026-03-11
# File: src/scitex/stats/_integration.py
"""SciTeX-specific stats integration.

Bundle interop, figrecipe integration, and conversion utilities.
These stay in scitex-python because they depend on scitex.io.bundle.
"""

import uuid

# =============================================================================
# Bundle Schema (scitex.io.bundle.Stats)
# =============================================================================

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

        Legacy flat format:
        - name: "Control vs Treatment"
        - method: "t-test"
        - p_value: 0.003
        - effect_size: 1.21
        - ci95: [0.5, 1.8]

        New nested format (from test functions):
        - method: {"name": "t-test", "variant": "independent"}
        - results: {"statistic": 2.5, "statistic_name": "t", "p_value": 0.01}

    Returns
    -------
    Stats
        Stats object suitable for bundle storage.
    """
    if not BUNDLE_AVAILABLE:
        raise ImportError("scitex.io.bundle is required for Stats conversion")

    from scitex.io.bundle._stats._dataclasses._Stats import (
        Analysis,
        EffectSize,
        StatMethod,
        StatResult,
    )

    method_data = result.get("method", {})
    if isinstance(method_data, str):
        method = StatMethod(name=method_data, variant=None, parameters={})
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
        method = StatMethod(
            name=method_data.get("name", "unknown"),
            variant=method_data.get("variant"),
            parameters=method_data.get("parameters", {}),
        )
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
# Bundle Save/Load
# =============================================================================


def save_stats(comparisons, path, metadata=None, as_zip=False):
    """Save statistical results as a SciTeX bundle.

    Parameters
    ----------
    comparisons : list of dict
        List of comparison results.
    path : str or Path
        Output path.
    metadata : dict, optional
        Additional metadata.
    as_zip : bool, optional
        If True, save as ZIP archive.

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

    bundle = Bundle(p, create=True, bundle_type="stats")

    if comparisons:
        if isinstance(comparisons[0], dict):
            stats = Stats(analyses=[])
            for comp in comparisons:
                analysis_stats = test_result_to_stats(comp)
                stats.analyses.extend(analysis_stats.analyses)
            bundle.stats = stats
        else:
            bundle.stats = comparisons

    bundle.save()
    return p


def load_stats(path):
    """Load a stats bundle.

    Parameters
    ----------
    path : str or Path
        Path to bundle.

    Returns
    -------
    dict
        Stats data with 'comparisons' and 'metadata'.
    """
    from scitex.io.bundle import Bundle

    bundle = Bundle(path)

    comparisons = []
    if bundle.stats and bundle.stats.analyses:
        for analysis in bundle.stats.analyses:
            ad = analysis.to_dict()
            p_val = ad.get("results", {}).get("p_value", 1.0)
            es_data = ad.get("results", {}).get("effect_size", {})
            es_val = es_data.get("value", 0.0) if es_data else 0.0
            ci = [es_data.get("ci_lower"), es_data.get("ci_upper")] if es_data else []
            ci = [v for v in ci if v is not None]

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
        "metadata": bundle.node.to_dict() if bundle.node else {},
    }


# =============================================================================
# Figrecipe Integration
# =============================================================================

from ._figrecipe_integration import (  # noqa: E402
    annotate,
    load_and_annotate,
    to_figrecipe,
)

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

# EOF
