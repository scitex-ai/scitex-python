#!/usr/bin/env python3
# Timestamp: "2026-01-19 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex-code/src/scitex/plt/__init__.py
"""
SciTeX plt module - Publication-quality plotting via figrecipe.

Usage
-----
>>> import scitex.plt as plt
>>> fig, ax = plt.subplots()
>>> ax.plot([1, 2, 3], [1, 4, 9])
>>> plt.save(fig, "figure.png")
"""

import os

# Set branding BEFORE importing figrecipe
os.environ.setdefault("FIGRECIPE_BRAND", "scitex.plt")
os.environ.setdefault("FIGRECIPE_ALIAS", "plt")

# Map SCITEX_PLT_* → FIGRECIPE_* (user-facing prefix takes priority)
_ENV_MAPPINGS = [
    ("SCITEX_PLT_DEBUG_MODE", "FIGRECIPE_DEBUG_MODE"),
    ("SCITEX_PLT_DEV_REPRESENTATIVE_PLOTS", "FIGRECIPE_DEV_REPRESENTATIVE_PLOTS"),
]
for _stx_key, _fr_key in _ENV_MAPPINGS:
    _val = os.environ.get(_stx_key) or os.environ.get(_fr_key)
    if _val:
        os.environ[_fr_key] = _val
try:
    import figrecipe as _fr

    _FIGRECIPE_AVAILABLE = True
except ImportError:
    _FIGRECIPE_AVAILABLE = False
    _fr = None

# Standard library and matplotlib imports
import matplotlib.pyplot as _plt  # noqa: E402

from scitex import logging as _logging  # noqa: E402

_logger = _logging.getLogger(__name__)

__FILE__ = __file__
__DIR__ = os.path.dirname(__FILE__)

# ============================================================================
# Re-export figrecipe public API with scitex branding
# ============================================================================
if _FIGRECIPE_AVAILABLE:
    # Core public API
    from figrecipe import (
        Diagram,
        compose,
        crop,
        extract_data,
        gui,
        info,
        list_presets,
        load_bundle,
        load_style,
        reproduce,
        reproduce_bundle,
        save,
        save_bundle,
        subplots,
        unload_style,
        validate,
    )
    from figrecipe import __version__ as _figrecipe_version

    # Backward compatibility alias
    edit = gui

    # Internal imports (not part of figrecipe public API)
    from figrecipe._api._notebook import enable_svg
    from figrecipe._api._seaborn_proxy import sns
    from figrecipe._api._style_manager import STYLE, apply_style
    from figrecipe._composition import align_panels, align_smart, distribute_panels

    # Backward compatibility alias
    smart_align = align_smart
    from figrecipe._graph._presets import get_preset as get_graph_preset
    from figrecipe._graph._presets import list_presets as list_graph_presets
    from figrecipe._graph._presets import register_preset as register_graph_preset

    # Also export load as alias for reproduce
    load = reproduce
else:
    # Provide stub versions when figrecipe is not available
    _figrecipe_version = "0.0.0"

    def _not_available(*args, **kwargs):
        raise ImportError(
            "figrecipe is required for this feature. Install with: pip install figrecipe"
        )

    Diagram = _not_available
    STYLE = None
    load_style = _not_available
    unload_style = _not_available
    list_presets = _not_available
    apply_style = _not_available
    subplots = _not_available
    save = _not_available
    reproduce = _not_available
    load = _not_available
    crop = _not_available
    validate = _not_available
    extract_data = _not_available
    info = _not_available
    gui = _not_available
    edit = _not_available  # Backward compatibility alias
    compose = _not_available
    align_panels = _not_available
    distribute_panels = _not_available
    align_smart = _not_available
    smart_align = _not_available  # Backward compatibility alias
    sns = None
    enable_svg = _not_available
    save_bundle = _not_available
    load_bundle = _not_available
    reproduce_bundle = _not_available
    get_graph_preset = _not_available
    list_graph_presets = _not_available
    register_graph_preset = _not_available

# ============================================================================
# Local scitex submodules (kept for compatibility)
# ============================================================================
try:
    from ._tpl import termplot
except ImportError:
    termplot = None

# Backward compatibility: expose styles submodule (deprecated, use figrecipe)
from . import ax, color, gallery, styles, utils  # noqa: E402

# Auto-configure matplotlib with SciTeX defaults on import
from ._auto_config import configure as _configure  # noqa: E402

# Import draw_graph from figrecipe integration (handles AxisWrapper)
from ._figrecipe_integration import draw_graph  # noqa: E402

# Spec building and rendering (moved from Django)
from ._render import render_spec_to_bytes  # noqa: E402
from ._spec_builders import (  # noqa: E402
    ALL_KINDS,
    DATA_KINDS,
    KIND_ALIASES,
    LABEL_KINDS,
    MATRIX_KINDS,
    XY_KINDS,
    build_spec,
    build_spec_from_csv,
)
from .styles import presets  # noqa: E402

_configure(_FIGRECIPE_AVAILABLE, load_style, color)


# ============================================================================
# SciTeX-specific wrapper functions (for AxisWrapper/FigWrapper compatibility)
# ============================================================================


def figure(*args, **kwargs):
    """Create a figure that returns a FigWrapper.

    This is the scitex-specific figure function that creates FigWrapper
    objects for compatibility with scitex.plt.ax utilities.

    For figrecipe-style recording figures, use subplots() instead.
    """
    from ._subplots._FigWrapper import FigWrapper

    fig_mpl = _plt.figure(*args, **kwargs)
    return FigWrapper(fig_mpl)


def tight_layout(**kwargs):
    """Apply tight layout to current figure with colorbar compatibility handling.

    This function calls tight_layout on the current figure and gracefully handles:
    1. UserWarning: "The figure layout has changed to tight" - informational only
    2. RuntimeError: Colorbar layout incompatibility - occurs when colorbars exist with old engine

    Parameters
    ----------
    **kwargs
        All keyword arguments are passed to matplotlib.pyplot.tight_layout()
    """
    import warnings

    with warnings.catch_warnings():
        warnings.filterwarnings(
            "ignore", message="The figure layout has changed to tight"
        )
        try:
            _plt.tight_layout(**kwargs)
        except RuntimeError as e:
            # Silently handle colorbar layout engine incompatibility
            if "Colorbar layout" not in str(e):
                raise


def colorbar(mappable=None, cax=None, ax=None, **kwargs):
    """
    Create a colorbar, automatically unwrapping SciTeX AxisWrapper objects.

    This function handles both regular matplotlib axes and SciTeX AxisWrapper
    objects transparently, making it a drop-in replacement for plt.colorbar().

    Parameters
    ----------
    mappable : ScalarMappable, optional
        The image, contour set, etc. to which the colorbar applies.
    cax : Axes, optional
        Axes into which the colorbar will be drawn.
    ax : Axes or AxisWrapper or list thereof, optional
        Parent axes from which space for the colorbar will be stolen.
    **kwargs
        Additional keyword arguments passed to matplotlib.pyplot.colorbar()

    Returns
    -------
    Colorbar
        The created colorbar object
    """
    # Unwrap ax if it's a SciTeX AxisWrapper
    if ax is not None:
        if hasattr(ax, "__iter__") and not isinstance(ax, str):
            # Handle list/array of axes
            ax = [a._axis_mpl if hasattr(a, "_axis_mpl") else a for a in ax]
        else:
            # Single axis
            ax = ax._axis_mpl if hasattr(ax, "_axis_mpl") else ax

    # Unwrap cax if provided
    if cax is not None:
        cax = cax._axis_mpl if hasattr(cax, "_axis_mpl") else cax

    # Call matplotlib's colorbar with unwrapped axes
    return _plt.colorbar(mappable=mappable, cax=cax, ax=ax, **kwargs)


def close(fig=None):
    """
    Close a figure, automatically unwrapping SciTeX FigWrapper objects.

    This function is a drop-in replacement for matplotlib.pyplot.close() that
    handles both regular matplotlib Figure objects and SciTeX FigWrapper objects.

    Parameters
    ----------
    fig : Figure, FigWrapper, int, str, or None
        The figure to close. Can be:
        - None: close the current figure
        - Figure or FigWrapper: close the specified figure
        - int: close figure with that number
        - str: close figure with that label, or 'all' to close all figures
    """
    if fig is None:
        _plt.close()
    elif isinstance(fig, (int, str)):
        _plt.close(fig)
    elif hasattr(fig, "_fig_mpl"):
        # FigWrapper object - unwrap and close
        _plt.close(fig._fig_mpl)
    elif hasattr(fig, "figure"):
        # Alternative attribute name (backward compatibility)
        _plt.close(fig.figure)
    elif hasattr(fig, "fig"):
        # figrecipe RecordingFigure - unwrap and close
        _plt.close(fig.fig)
    else:
        # Assume it's a matplotlib Figure
        _plt.close(fig)


# ============================================================================
# Public API
# ============================================================================

__all__ = [
    # Figrecipe classes
    "Diagram",
    # Figrecipe core (re-exported with branding)
    "subplots",
    "save",
    "reproduce",
    "load",  # Alias for reproduce
    "crop",
    "validate",
    "extract_data",
    "info",
    "gui",
    "edit",  # Backward compatibility alias for gui
    # Bundle support
    "save_bundle",
    "load_bundle",
    "reproduce_bundle",
    # Style management
    "STYLE",
    "load_style",
    "unload_style",
    "list_presets",
    "apply_style",
    # Composition
    "compose",
    "align_panels",
    "distribute_panels",
    "align_smart",
    "smart_align",  # Backward compatibility alias for align_smart
    # Spec building and rendering
    "build_spec",
    "build_spec_from_csv",
    "render_spec_to_bytes",
    "XY_KINDS",
    "DATA_KINDS",
    "LABEL_KINDS",
    "MATRIX_KINDS",
    "ALL_KINDS",
    "KIND_ALIASES",
    # Graph visualization
    "draw_graph",
    "get_graph_preset",
    "list_graph_presets",
    "register_graph_preset",
    # Extensions
    "sns",
    "enable_svg",
    # SciTeX-specific wrappers
    "figure",
    "colorbar",
    "close",
    "tight_layout",
    # Local submodules
    "ax",
    "color",
    "gallery",
    "utils",
    "styles",
    "presets",
    "termplot",
]


def __getattr__(name):
    """Fallback to matplotlib.pyplot for any missing attributes.

    This makes scitex.plt a complete drop-in replacement for matplotlib.pyplot.
    """
    if hasattr(_plt, name):
        return getattr(_plt, name)
    raise AttributeError(f"module 'scitex.plt' has no attribute '{name}'")


def __dir__():
    """Provide comprehensive directory listing including matplotlib.pyplot functions."""
    local_attrs = list(__all__)
    # Add matplotlib.pyplot attributes
    mpl_attrs = [attr for attr in dir(_plt) if not attr.startswith("_")]
    local_attrs.extend(mpl_attrs)
    return sorted(set(local_attrs))


# EOF
