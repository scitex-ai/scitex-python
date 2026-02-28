#!/usr/bin/env python3
# File: /home/ywatanabe/proj/scitex-python/src/scitex/plt/__init__.py
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

# Map SCITEX_PLT_* -> FIGRECIPE_* (user-facing prefix takes priority)
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

    # Additional figrecipe public API re-exports
    from figrecipe import (
        align_panels,
        align_smart,
        distribute_panels,
        get_graph_preset,
        list_graph_presets,
        register_graph_preset,
    )
    from figrecipe.utils import STYLE, apply_style, enable_svg, sns

    # Backward compatibility alias
    smart_align = align_smart

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
# Local scitex submodules
# ============================================================================
try:
    from ._tpl import termplot
except ImportError:
    termplot = None

from . import color, gallery, styles, utils  # noqa: E402

# Auto-configure matplotlib with SciTeX defaults on import
from ._auto_config import configure as _configure  # noqa: E402

# Import draw_graph from figrecipe integration
from ._figrecipe_integration import draw_graph  # noqa: E402

# Spec building and rendering
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
# SciTeX-specific wrapper functions
# ============================================================================


def tight_layout(**kwargs):
    """Apply tight layout to current figure with colorbar compatibility handling."""
    import warnings

    with warnings.catch_warnings():
        warnings.filterwarnings(
            "ignore", message="The figure layout has changed to tight"
        )
        try:
            _plt.tight_layout(**kwargs)
        except RuntimeError as e:
            if "Colorbar layout" not in str(e):
                raise


def colorbar(mappable=None, cax=None, ax=None, **kwargs):
    """Create a colorbar, unwrapping wrapper axes if needed.

    Parameters
    ----------
    mappable : ScalarMappable, optional
        The image, contour set, etc. to which the colorbar applies.
    cax : Axes, optional
        Axes into which the colorbar will be drawn.
    ax : Axes or list thereof, optional
        Parent axes from which space for the colorbar will be stolen.
    **kwargs
        Additional keyword arguments passed to matplotlib.pyplot.colorbar()

    Returns
    -------
    Colorbar
        The created colorbar object
    """

    def _unwrap(a):
        """Unwrap any axes wrapper to raw matplotlib Axes."""
        for attr in ("_ax", "_axis_mpl"):
            if hasattr(a, attr):
                return getattr(a, attr)
        return a

    if ax is not None:
        if hasattr(ax, "__iter__") and not isinstance(ax, str):
            ax = [_unwrap(a) for a in ax]
        else:
            ax = _unwrap(ax)

    if cax is not None:
        cax = _unwrap(cax)

    return _plt.colorbar(mappable=mappable, cax=cax, ax=ax, **kwargs)


def close(fig=None):
    """Close a figure, unwrapping wrapper objects if needed.

    Parameters
    ----------
    fig : Figure, RecordingFigure, int, str, or None
        The figure to close.
    """
    if fig is None:
        _plt.close()
    elif isinstance(fig, (int, str)):
        _plt.close(fig)
    elif hasattr(fig, "fig"):
        # figrecipe RecordingFigure
        _plt.close(fig.fig)
    elif hasattr(fig, "_fig_mpl"):
        # Legacy FigWrapper (backward compat)
        _plt.close(fig._fig_mpl)
    else:
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
    "colorbar",
    "close",
    "tight_layout",
    # Local submodules
    "color",
    "gallery",
    "utils",
    "styles",
    "presets",
    "termplot",
]


def __getattr__(name):
    """Fallback to matplotlib.pyplot for any missing attributes."""
    if hasattr(_plt, name):
        return getattr(_plt, name)
    raise AttributeError(f"module 'scitex.plt' has no attribute '{name}'")


def __dir__():
    """Provide directory listing including matplotlib.pyplot functions."""
    local_attrs = list(__all__)
    mpl_attrs = [attr for attr in dir(_plt) if not attr.startswith("_")]
    local_attrs.extend(mpl_attrs)
    return sorted(set(local_attrs))


# EOF
