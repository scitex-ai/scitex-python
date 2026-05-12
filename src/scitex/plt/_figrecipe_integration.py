#!/usr/bin/env python3
# Timestamp: "2026-01-12 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex-code/src/scitex/plt/_figrecipe_integration.py
"""Figrecipe integration for scitex.plt (graph visualization, editor)."""

from typing import Any, Callable, Dict, Optional, Union

from scitex_dev import try_import_optional

fr = try_import_optional("figrecipe", extra="plt", pkg="scitex")
_fr_draw_graph = try_import_optional(
    "figrecipe._graph", "draw_graph", extra="plt", pkg="scitex"
)
_AVAILABLE = fr is not None and _fr_draw_graph is not None


def draw_graph(
    ax,
    G,
    *,
    layout: str = "spring",
    pos: Optional[Dict] = None,
    seed: int = 42,
    node_size: Union[str, Callable, float] = 100,
    node_color: Union[str, Callable, Any] = "#3498db",
    node_alpha: float = 0.8,
    edge_width: Union[str, Callable, float] = 1.0,
    edge_color: Union[str, Callable, Any] = "gray",
    edge_alpha: float = 0.4,
    arrows: Optional[bool] = None,
    labels: Union[bool, Dict, str] = False,
    font_size: float = 6,
    colormap: str = "viridis",
    **kwargs,
) -> Dict[str, Any]:
    """Draw a NetworkX graph on axes.

    Parameters
    ----------
    ax : Axes or AxisWrapper
        The axes to draw on.
    G : networkx.Graph
        The graph to draw.
    layout : str
        Layout: 'spring', 'circular', 'kamada_kawai', 'shell', 'hierarchical'.
    pos : dict, optional
        Pre-computed positions {node: (x, y)}.
    seed : int
        Random seed for layout.
    node_size, node_color, node_alpha : styling
        Node appearance settings.
    edge_width, edge_color, edge_alpha : styling
        Edge appearance settings.
    arrows : bool, optional
        Draw arrows (auto-detect if None).
    labels : bool, dict, or str
        Node labels.
    font_size : float
        Label font size (6pt default for publication).
    colormap : str
        Colormap for numeric node colors.

    Returns
    -------
    dict
        {'pos': positions, 'node_collection': ..., 'edge_collection': ...}
    """
    if not _AVAILABLE:
        raise ImportError("figrecipe >= 0.13.0 required: pip install figrecipe")

    # Unwrap scitex AxisWrapper
    ax_mpl = getattr(ax, "_axis_mpl", getattr(ax, "_ax", ax))

    return _fr_draw_graph(
        ax_mpl,
        G,
        layout=layout,
        pos=pos,
        seed=seed,
        node_size=node_size,
        node_color=node_color,
        node_alpha=node_alpha,
        edge_width=edge_width,
        edge_color=edge_color,
        edge_alpha=edge_alpha,
        arrows=arrows,
        labels=labels,
        font_size=font_size,
        colormap=colormap,
        **kwargs,
    )


def edit(source=None, style=None, port: int = 5050, **kwargs):
    """Launch interactive GUI editor for figure styling.

    Parameters
    ----------
    source : RecordingFigure, str, Path, or None
        Figure object or path to .yaml recipe.
    style : str or dict, optional
        Style preset or dict.
    port : int
        Server port (default: 5050).
    **kwargs
        Additional args (host, open_browser, desktop, etc.)

    Returns
    -------
    dict
        Style overrides after editing session.
    """
    if not _AVAILABLE:
        raise ImportError("figrecipe >= 0.13.0 required: pip install figrecipe")

    return fr.edit(source, style=style, port=port, **kwargs)


__all__ = ["draw_graph", "edit"]

# EOF
