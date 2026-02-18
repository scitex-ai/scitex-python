#!/usr/bin/env python3
# Timestamp: "2026-01-12 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex-code/src/scitex/stats/_figrecipe_integration.py
"""Figrecipe integration for statistical annotations on plots."""

from typing import Any, Dict, List, Optional, Union

try:
    from figrecipe._integrations._scitex_stats import (  # not yet in public API
        load_stats_bundle as _fr_load_bundle,
    )
    from figrecipe.utils import annotate_from_stats as _fr_annotate
    from figrecipe.utils import from_scitex_stats as _fr_convert

    _AVAILABLE = True
except ImportError:
    _AVAILABLE = False


def to_figrecipe(
    stats_result: Union[Dict[str, Any], List[Dict[str, Any]]],
) -> Dict[str, Any]:
    """Convert scitex.stats result(s) to figrecipe format.

    Parameters
    ----------
    stats_result : dict or list of dict
        Statistical result(s) from scitex.stats functions.

    Returns
    -------
    dict
        Figrecipe-compatible format with 'comparisons' list.
    """
    if not _AVAILABLE:
        raise ImportError("figrecipe >= 0.13.0 required: pip install figrecipe")
    return _fr_convert(stats_result)


def annotate(
    ax,
    stats: Union[Dict[str, Any], List[Dict[str, Any]]],
    positions: Optional[Dict[str, float]] = None,
    style: str = "stars",
    **kwargs,
) -> List[Any]:
    """Add statistical annotations to a plot.

    Parameters
    ----------
    ax : Axes or AxisWrapper
        The axes to annotate.
    stats : dict or list of dict
        Statistical results (auto-converted if needed).
    positions : dict, optional
        Group name to x position mapping.
    style : str
        'stars', 'p_value', or 'both'.

    Returns
    -------
    list
        Created matplotlib artist objects.
    """
    if not _AVAILABLE:
        raise ImportError("figrecipe >= 0.13.0 required: pip install figrecipe")

    # Convert if needed
    if isinstance(stats, list) or "comparisons" not in stats:
        stats = _fr_convert(stats)

    # Unwrap scitex AxisWrapper
    ax_mpl = getattr(ax, "_axis_mpl", getattr(ax, "_ax", ax))

    return _fr_annotate(ax_mpl, stats, positions=positions, style=style, **kwargs)


def load_and_annotate(
    ax,
    path: str,
    positions: Optional[Dict[str, float]] = None,
    style: str = "stars",
    **kwargs,
) -> List[Any]:
    """Load stats from bundle file and annotate plot.

    Parameters
    ----------
    ax : Axes or AxisWrapper
        The axes to annotate.
    path : str
        Path to .statsz or .zip bundle.
    positions : dict, optional
        Group name to x position mapping.
    style : str
        'stars', 'p_value', or 'both'.

    Returns
    -------
    list
        Created matplotlib artist objects.
    """
    if not _AVAILABLE:
        raise ImportError("figrecipe >= 0.13.0 required: pip install figrecipe")

    fr_stats = _fr_load_bundle(path)
    return annotate(ax, fr_stats, positions=positions, style=style, **kwargs)


__all__ = ["to_figrecipe", "annotate", "load_and_annotate"]

# EOF
