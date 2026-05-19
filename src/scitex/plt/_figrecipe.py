#!/usr/bin/env python3
# Timestamp: "2026-01-01 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex-code/src/scitex/plt/_figrecipe.py
# ----------------------------------------
"""
Figrecipe integration for scitex.

This module provides integration with figrecipe for reproducible matplotlib figures.
Uses csv_format="single" by default for backward compatibility with scitex's
SigmaPlot-compatible CSV format.

Usage
-----
>>> import scitex.plt as splt
>>> fig, ax = splt.subplots()
>>> ax.plot([1, 2, 3], [4, 5, 6], id='data')
>>> splt.save_recipe(fig, 'figure.yaml')  # Saves recipe with single CSV
"""

from pathlib import Path
from typing import Any, Dict, Literal, Optional, Tuple, Union

from scitex import logging

logger = logging.getLogger(__name__)

# Check if figrecipe is available
from scitex_dev import try_import_optional

fr = try_import_optional("figrecipe", extra="plt", pkg="scitex")
FIGRECIPE_AVAILABLE = fr is not None


def check_figrecipe_available() -> bool:
    """Check if figrecipe is installed."""
    return FIGRECIPE_AVAILABLE


def subplots(
    nrows: int = 1,
    ncols: int = 1,
    **kwargs,
) -> Tuple[Any, Any]:
    """Create recording-enabled subplots using figrecipe.

    This is a wrapper around figrecipe.subplots() that creates
    figures with recording capabilities for reproducibility.

    Parameters
    ----------
    nrows, ncols : int
        Number of rows and columns.
    **kwargs
        Additional arguments passed to figrecipe.subplots().

    Returns
    -------
    fig : RecordingFigure
        Figrecipe's wrapped figure.
    axes : RecordingAxes or ndarray
        Wrapped axes.

    Raises
    ------
    ImportError
        If figrecipe is not installed.
    """
    if not FIGRECIPE_AVAILABLE:
        raise ImportError(
            "figrecipe is not installed. Install with: pip install figrecipe"
        )

    return fr.subplots(nrows, ncols, **kwargs)


def save_recipe(
    fig,
    path: Union[str, Path],
    csv_format: Literal["single", "separate"] = "single",
    data_format: Literal["csv", "npz", "inline"] = "csv",
    validate: bool = True,
    verbose: bool = True,
    **kwargs,
) -> Optional[Tuple[Path, Path]]:
    """Save figure recipe using figrecipe with scitex-compatible CSV format.

    This function saves a matplotlib figure as a reproducible recipe using
    figrecipe. By default, uses csv_format="single" for backward compatibility
    with scitex's SigmaPlot-compatible CSV format.

    Parameters
    ----------
    fig : matplotlib.figure.Figure or RecordingFigure
        The figure to save.
    path : str or Path
        Output path (.yaml for recipe, .png/.pdf for image+recipe).
    csv_format : str
        CSV format: 'single' (scitex-compatible, default) or 'separate'.
        - 'single': All columns in one CSV with scitex naming convention
        - 'separate': One CSV per variable (figrecipe default)
    data_format : str
        Data format: 'csv' (default), 'npz', or 'inline'.
    validate : bool
        If True (default), validate reproducibility after saving.
    verbose : bool
        If True (default), print save status.
    **kwargs
        Additional arguments passed to figrecipe.save().

    Returns
    -------
    tuple or None
        (image_path, yaml_path) if successful, None if figrecipe unavailable.

    Examples
    --------
    >>> import scitex.plt as splt
    >>> fig, ax = splt.subplots()
    >>> ax.plot([1, 2, 3], [4, 5, 6])
    >>> splt.save_recipe(fig, 'output.yaml')  # Single CSV format (scitex-compatible)
    >>> splt.save_recipe(fig, 'output.yaml', csv_format='separate')  # Separate CSVs
    """
    if not FIGRECIPE_AVAILABLE:
        logger.warning(
            "figrecipe is not installed. Recipe not saved. "
            "Install with: pip install figrecipe"
        )
        return None

    path = Path(path)

    # Handle different figure types
    # If it's a scitex FigWrapper, extract the matplotlib figure
    if hasattr(fig, "_fig_mpl"):
        mpl_fig = fig._fig_mpl
    elif hasattr(fig, "figure"):
        mpl_fig = fig.figure
    else:
        mpl_fig = fig

    # Check if fig is already a figrecipe RecordingFigure
    if hasattr(fig, "_recorder"):
        # Already a RecordingFigure, use figrecipe's save directly
        return fr.save(
            fig,
            path,
            data_format=data_format,
            csv_format=csv_format,
            validate=validate,
            verbose=verbose,
            **kwargs,
        )

    # For regular matplotlib figures, we need to wrap them first
    # This requires re-creating the figure with figrecipe
    logger.warning(
        "Figure is not a RecordingFigure. For full recipe support, "
        "create figures with fr.subplots() or splt.subplots_recipe()."
    )
    return None


def load_recipe(path: Union[str, Path]) -> Tuple[Any, Any]:
    """Load and reproduce a figure from a recipe file.

    Parameters
    ----------
    path : str or Path
        Path to .yaml recipe file.

    Returns
    -------
    fig : matplotlib.figure.Figure
        Reproduced figure.
    axes : Axes or list of Axes
        Reproduced axes.

    Raises
    ------
    ImportError
        If figrecipe is not installed.
    """
    if not FIGRECIPE_AVAILABLE:
        raise ImportError(
            "figrecipe is not installed. Install with: pip install figrecipe"
        )

    return fr.reproduce(path)


def recipe_info(path: Union[str, Path]) -> Dict[str, Any]:
    """Get information about a recipe without reproducing.

    Parameters
    ----------
    path : str or Path
        Path to .yaml recipe file.

    Returns
    -------
    dict
        Recipe information including figure settings, calls, etc.

    Raises
    ------
    ImportError
        If figrecipe is not installed.
    """
    if not FIGRECIPE_AVAILABLE:
        raise ImportError(
            "figrecipe is not installed. Install with: pip install figrecipe"
        )

    return fr.info(path)


# Convenience aliases
reproduce = load_recipe
info = recipe_info


__all__ = [
    "FIGRECIPE_AVAILABLE",
    "check_figrecipe_available",
    "subplots",
    "save_recipe",
    "load_recipe",
    "reproduce",
    "recipe_info",
    "info",
]

# EOF
