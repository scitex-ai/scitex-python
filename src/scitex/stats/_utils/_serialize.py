#!/usr/bin/env python3
# Timestamp: "2026-02-17"
# File: scitex/stats/_utils/_serialize.py
"""JSON-safe serialization for statistical test results.

Converts numpy types to Python natives, handles inf/nan,
adds key aliases and formatted summary strings.
"""

from __future__ import annotations

import os
from typing import Any, Dict

import numpy as np

__FILE__ = __file__
__DIR__ = os.path.dirname(__FILE__)


def to_json_safe(result: Dict[str, Any]) -> Dict[str, Any]:
    """Convert a test result dict to JSON-serializable Python types.

    Handles numpy scalar/array conversion, inf/nan to None, key aliases
    for common frontend expectations, and builds a formatted summary string.

    Parameters
    ----------
    result : dict
        Raw test result dictionary from any ``stx.stats.test_*()`` function.

    Returns
    -------
    dict
        JSON-safe dict with consistent keys and a ``formatted`` summary.

    Examples
    --------
    >>> import numpy as np
    >>> raw = {"pvalue": np.float64(0.023), "statistic": np.float64(2.45),
    ...        "stat_symbol": "t", "effect_size": np.float64(0.85),
    ...        "effect_size_metric": "Cohen's d", "stars": "*"}
    >>> safe = to_json_safe(raw)
    >>> type(safe["pvalue"])
    <class 'float'>
    >>> "p_value" in safe
    True
    >>> "formatted" in safe
    True
    """
    out: Dict[str, Any] = {}
    for k, v in result.items():
        if isinstance(v, np.bool_):
            out[k] = bool(v)
        elif isinstance(v, (np.floating, np.integer)):
            fv = float(v)
            out[k] = None if (np.isinf(fv) or np.isnan(fv)) else fv
        elif isinstance(v, float) and (np.isinf(v) or np.isnan(v)):
            out[k] = None
        elif isinstance(v, np.ndarray):
            out[k] = v.tolist()
        else:
            out[k] = v

    # Key aliases for frontend compatibility
    if "pvalue" in out and "p_value" not in out:
        out["p_value"] = out["pvalue"]
    if "test_method" in out and "test" not in out:
        out["test"] = out["test_method"]

    # Build formatted summary string
    if "formatted" not in out and "statistic" in out and "p_value" in out:
        symbol = out.get("stat_symbol", "stat")
        stat_val = out["statistic"]
        p_val = out["p_value"]
        parts = [
            f"{symbol} = {stat_val:.3f}" if stat_val is not None else f"{symbol} = N/A",
            f"p = {p_val:.4f}" if p_val is not None else "p = N/A",
        ]
        if "effect_size" in out and out["effect_size"] is not None:
            metric = out.get("effect_size_metric", "d")
            parts.append(f"{metric} = {out['effect_size']:.3f}")
        if "stars" in out:
            parts.append(out["stars"])
        out["formatted"] = ", ".join(parts)

    return out


__all__ = ["to_json_safe"]

# EOF
