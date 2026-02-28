"""Pluggable visualization for citation graphs.

Supports multiple rendering backends with automatic fallback:
    figrecipe > scitex.plt > matplotlib > pyvis

Example
-------
    >>> from scitex.scholar.citation_graph import CitationGraphBuilder, plot_citation_graph
    >>> builder = CitationGraphBuilder("/path/to/crossref.db")
    >>> graph = builder.build("10.1038/s41586-020-2008-3", top_n=20)
    >>> fig = plot_citation_graph(graph)                    # auto backend
    >>> fig = plot_citation_graph(graph, backend="pyvis", output="network.html")
"""

from typing import Any, Dict, Optional

# ── Backend availability flags ───────────────────────────────────────────────

try:
    from figrecipe import get_graph_preset as _fr_get_preset
    from figrecipe._graph import draw_graph as _fr_draw_graph  # not yet in public API

    _FIGRECIPE_AVAILABLE = True
except ImportError:
    _FIGRECIPE_AVAILABLE = False

try:
    from scitex.plt._figrecipe_integration import draw_graph as _stx_draw_graph

    _SCITEX_PLT_AVAILABLE = True
except ImportError:
    _SCITEX_PLT_AVAILABLE = False

try:
    from pyvis.network import Network as _PyvisNetwork

    _PYVIS_AVAILABLE = True
except ImportError:
    _PYVIS_AVAILABLE = False

_MATPLOTLIB_AVAILABLE = True  # always available (core dependency)

# Backend resolution order
_BACKEND_PRIORITY = ["figrecipe", "scitex.plt", "matplotlib", "pyvis"]


def list_backends() -> Dict[str, bool]:
    """List available visualization backends.

    Returns
    -------
    dict
        Mapping of backend name to availability.
    """
    return {
        "figrecipe": _FIGRECIPE_AVAILABLE,
        "scitex.plt": _SCITEX_PLT_AVAILABLE,
        "matplotlib": _MATPLOTLIB_AVAILABLE,
        "pyvis": _PYVIS_AVAILABLE,
    }


def _resolve_backend(backend: str) -> str:
    """Resolve 'auto' to the best available backend."""
    if backend != "auto":
        available = list_backends()
        if backend not in available:
            raise ValueError(
                f"Unknown backend '{backend}'. Available: {list(available.keys())}"
            )
        if not available[backend]:
            raise ImportError(
                f"Backend '{backend}' is not available. "
                f"Available backends: "
                f"{[k for k, v in available.items() if v]}"
            )
        return backend

    for name in _BACKEND_PRIORITY:
        if list_backends()[name]:
            return name

    return "matplotlib"  # fallback (always available)


# ── Backend implementations ──────────────────────────────────────────────────


def _plot_figrecipe(G, output=None, **kwargs):
    """Render with figrecipe (publication-quality static)."""
    import matplotlib.pyplot as plt

    preset = _fr_get_preset("citation")
    merged = {**preset, **kwargs}

    fig, ax = plt.subplots(1, 1, figsize=kwargs.pop("figsize", (8, 6)))
    result = _fr_draw_graph(ax, G, **merged)

    if output:
        fig.savefig(output, dpi=kwargs.get("dpi", 150), bbox_inches="tight")

    return {"fig": fig, "ax": ax, "pos": result["pos"], "backend": "figrecipe"}


def _plot_scitex_plt(G, output=None, **kwargs):
    """Render with scitex.plt (AxisWrapper + CSV auto-export)."""
    import scitex.plt as stx_plt

    preset = _fr_get_preset("citation") if _FIGRECIPE_AVAILABLE else {}
    merged = {**preset, **kwargs}

    fig, ax = stx_plt.subplots()
    result = _stx_draw_graph(ax, G, **merged)

    if output:
        import scitex.io

        scitex.io.save(fig, output)

    return {"fig": fig, "ax": ax, "pos": result["pos"], "backend": "scitex.plt"}


def _plot_matplotlib(G, output=None, **kwargs):  # noqa: C901
    """Render with raw matplotlib + networkx (no external deps)."""
    import matplotlib.pyplot as plt
    import networkx as nx

    fig, ax = plt.subplots(1, 1, figsize=kwargs.pop("figsize", (8, 6)))

    layout = kwargs.pop("layout", "spring")
    seed = kwargs.pop("seed", 42)

    # Compute layout
    layout_funcs = {
        "spring": lambda g: nx.spring_layout(g, seed=seed),
        "circular": nx.circular_layout,
        "kamada_kawai": nx.kamada_kawai_layout,
        "shell": nx.shell_layout,
        "spectral": nx.spectral_layout,
    }
    layout_fn = layout_funcs.get(layout, layout_funcs["spring"])
    pos = layout_fn(G)

    # Node sizing by citations
    citations = [G.nodes[n].get("citations", 1) for n in G.nodes()]
    max_c = max(citations) if citations else 1
    sizes = [50 + (c / max(max_c, 1)) * 250 for c in citations]

    # Node coloring by year
    years = [G.nodes[n].get("year", 0) for n in G.nodes()]

    # Draw
    nx.draw_networkx_edges(G, pos, alpha=0.3, ax=ax)
    nx.draw_networkx_nodes(
        G,
        pos,
        node_size=sizes,
        node_color=years if any(years) else "#3498db",
        cmap=plt.cm.viridis if any(years) else None,
        alpha=0.8,
        ax=ax,
    )

    # Labels: short titles
    labels = {n: G.nodes[n].get("short_title", n)[:20] for n in G.nodes()}
    nx.draw_networkx_labels(G, pos, labels=labels, font_size=5, ax=ax)

    ax.axis("off")

    if output:
        fig.savefig(output, dpi=kwargs.get("dpi", 150), bbox_inches="tight")

    return {"fig": fig, "ax": ax, "pos": pos, "backend": "matplotlib"}


def _plot_pyvis(G, output=None, **kwargs):
    """Render as interactive HTML with pyvis."""
    if output is None:
        raise ValueError("pyvis backend requires output path (HTML file)")

    net = _PyvisNetwork(
        height="750px",
        width="100%",
        bgcolor="#ffffff",
        font_color="black",
    )
    net.barnes_hut()

    for node_id in G.nodes():
        data = G.nodes[node_id]
        title = data.get("title", str(node_id))
        citations = data.get("citations", 0)
        year = data.get("year", "?")
        size = 10 + min(citations, 500) ** 0.5 * 2

        net.add_node(
            node_id,
            label=f"{title[:40]}...\n({year})",
            title=f"{title}\n{node_id}\nCitations: {citations}",
            size=size,
            color="#3498db" if citations > 50 else "#95a5a6",
        )

    for u, v in G.edges():
        net.add_edge(u, v)

    net.save_graph(str(output))
    return {"output": str(output), "backend": "pyvis"}


_BACKEND_DISPATCH = {
    "figrecipe": _plot_figrecipe,
    "scitex.plt": _plot_scitex_plt,
    "matplotlib": _plot_matplotlib,
    "pyvis": _plot_pyvis,
}


# ── Public API ───────────────────────────────────────────────────────────────


def plot_citation_graph(
    graph,
    backend: str = "auto",
    output: Optional[str] = None,
    **kwargs,
) -> Dict[str, Any]:
    """Visualize a citation graph with pluggable backends.

    Parameters
    ----------
    graph : CitationGraph or networkx.DiGraph
        Citation network to visualize. CitationGraph is auto-converted
        via ``to_networkx()``.
    backend : str
        Rendering backend: 'auto', 'figrecipe', 'scitex.plt',
        'matplotlib', or 'pyvis'. Default 'auto' picks the best available.
    output : str, optional
        Output file path. Required for 'pyvis' backend (HTML).
        For static backends, saves the figure to this path.
    **kwargs
        Backend-specific keyword arguments (layout, seed, figsize, etc.).

    Returns
    -------
    dict
        Backend-specific result. Static backends return
        ``{'fig', 'ax', 'pos', 'backend'}``.
        Pyvis returns ``{'output', 'backend'}``.
    """
    from .models import CitationGraph

    # Convert CitationGraph to NetworkX if needed
    if isinstance(graph, CitationGraph):
        G = graph.to_networkx()
    else:
        G = graph

    resolved = _resolve_backend(backend)
    return _BACKEND_DISPATCH[resolved](G, output=output, **kwargs)


__all__ = ["plot_citation_graph", "list_backends"]

# EOF
