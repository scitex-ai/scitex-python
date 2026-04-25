#!/usr/bin/env python3
# File: ./src/scitex/bridge/_helpers.py
# Time-stamp: "2024-12-09 11:00:00 (ywatanabe)"
"""
High-level helper functions for cross-module operations.

These helpers provide a unified API for common workflows that span
multiple modules, abstracting away backend-specific details.
"""

from typing import List, Literal, Union

# StatResult is now a dict - the GUI-specific StatResult is deprecated
StatResult = dict


def add_stats_from_results(
    target,
    stat_results: Union[StatResult, List[StatResult]],
    backend: Literal["auto", "plt", "vis"] = "auto",
    format_style: str = "asterisk",
    **kwargs,
):
    """
    Add statistical results to a figure or axes, auto-detecting backend.

    This is a high-level helper that works with both matplotlib axes
    and vis FigureModel, choosing the appropriate bridge function.

    Parameters
    ----------
    target : matplotlib.axes.Axes, scitex.plt.AxisWrapper, or FigureModel
        The target to add statistics to
    stat_results : StatResult or List[StatResult]
        Statistical result(s) to add
    backend : {"auto", "plt", "vis"}
        Backend to use. "auto" detects from target type:
        - matplotlib axes or scitex AxisWrapper → "plt"
        - FigureModel → "vis"
    format_style : str
        Format style for stat text ("asterisk", "compact", "detailed", "publication")
    **kwargs
        Additional arguments passed to the backend-specific function:
        - plt: passed to add_stat_to_axes (x, y, transform, etc.)
        - vis: passed to add_stats_to_figure_model (axes_index, auto_position, etc.)

    Returns
    -------
    target
        The modified target (for chaining)

    Examples
    --------
    >>> # With matplotlib axes
    >>> fig, ax = plt.subplots()
    >>> stat = create_stat_result("pearson", "r", 0.85, 0.001)
    >>> add_stats_from_results(ax, stat)

    >>> # With vis FigureModel
    >>> model = FigureModel(width_mm=170, height_mm=120, axes=[{}])
    >>> add_stats_from_results(model, [stat1, stat2], backend="vis")

    Notes
    -----
    Coordinate conventions differ between backends:
    - plt: uses axes coordinates (0-1 normalized) by default
    - vis: uses data coordinates

    For precise control, use the backend-specific functions directly:
    - scitex.bridge.add_stat_to_axes (plt backend)
    - scitex.bridge.add_stats_to_figure_model (vis backend)
    """
    # Normalize to list
    if isinstance(stat_results, StatResult):
        stat_results = [stat_results]

    # Auto-detect backend
    if backend == "auto":
        backend = _detect_backend(target)

    # Dispatch to appropriate function
    if backend == "plt":
        from scitex.bridge._stats_plt import add_stat_to_axes

        for stat in stat_results:
            add_stat_to_axes(target, stat, format_style=format_style, **kwargs)

    elif backend == "vis":
        from scitex.bridge._stats_vis import add_stats_to_figure_model

        add_stats_to_figure_model(
            target,
            stat_results,
            format_style=format_style,
            **kwargs,
        )

    else:
        raise ValueError(f"Unknown backend: {backend}. Use 'auto', 'plt', or 'vis'.")

    return target


def _detect_backend(target) -> Literal["plt", "vis"]:
    """
    Detect the appropriate backend from target type.

    Parameters
    ----------
    target : any
        The target object

    Returns
    -------
    str
        "plt" or "vis"
    """
    # Check for vis FigureModel
    try:
        from scitex.io.bundle.kinds._plot._models import FigureModel

        if isinstance(target, FigureModel):
            return "vis"
    except ImportError:
        pass

    # Check for matplotlib axes
    try:
        import matplotlib.axes

        if isinstance(target, matplotlib.axes.Axes):
            return "plt"
    except ImportError:
        pass

    # Check for scitex plt wrappers
    if hasattr(target, "_axes_mpl"):
        return "plt"
    if hasattr(target, "_axes_scitex"):
        return "plt"

    # Default to plt (most common case)
    return "plt"


__all__ = [
    "add_stats_from_results",
]


# EOF
