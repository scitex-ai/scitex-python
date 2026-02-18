#!/usr/bin/env python3
# Timestamp: 2026-01-24
# File: /home/ywatanabe/proj/scitex-code/src/scitex/_mcp_tools/diagram.py
"""Diagram module tools for FastMCP unified server.

This module delegates to figrecipe's diagram implementation for single source of truth.
All diagram_* tools are thin wrappers around figrecipe's canonical implementation.
"""

from __future__ import annotations

import os
from typing import Any, Dict, Literal, Optional  # noqa: F401


def register_diagram_tools(mcp) -> None:
    """Register diagram tools with FastMCP server.

    Delegates to figrecipe's diagram tools (canonical source).
    Tools are prefixed with 'diagram_' for scitex namespace consistency.
    """
    # Ensure branding is set before any figrecipe imports
    os.environ.setdefault("FIGRECIPE_BRAND", "scitex.diagram")
    os.environ.setdefault("FIGRECIPE_ALIAS", "diagram")

    # Check if figrecipe is available
    try:
        from figrecipe import Diagram

        _FIGRECIPE_AVAILABLE = True
    except ImportError:
        _FIGRECIPE_AVAILABLE = False

    if not _FIGRECIPE_AVAILABLE:

        @mcp.tool()
        def diagram_not_available() -> str:
            """[diagram] figrecipe not installed."""
            return "figrecipe is required for diagram tools. Install with: pip install figrecipe"

        return

    def _load_diagram(spec_dict, spec_path):
        """Load a Diagram from spec_dict or spec_path."""
        if spec_path:
            return Diagram.from_yaml(spec_path)
        elif spec_dict:
            return Diagram.from_dict(spec_dict)
        else:
            raise ValueError("Either spec_dict or spec_path must be provided")

    @mcp.tool()
    def diagram_create(
        spec_dict: Optional[Dict[str, Any]] = None,
        spec_path: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Create a diagram from a YAML specification file or dictionary.

        **PRIMARY DIAGRAM TOOL - Use this for creating diagrams.**

        This is the recommended entry point for diagram creation using SciTeX's
        publication-optimized diagram system. It generates both Mermaid and
        Graphviz representations from your specification.

        **Available Themes:**
        - MATPLOTLIB: Matplotlib color scheme
        - SCITEX: SciTeX publication theme (RECOMMENDED, DEFAULT)

        **Available Presets:**
        - workflow: Left-to-right flow, rounded boxes (process diagrams)
        - decision: Top-down flow, diamond nodes (flowcharts)
        - pipeline: Left-to-right flow, data cylinders (data pipelines)
        - scientific: Top-down flow, clean academic style (methods diagrams)

        Parameters
        ----------
        spec_dict : dict, optional
            Diagram specification as dictionary. Required keys: nodes, edges.
            Optional keys: metadata, preset, groups, theme.

        spec_path : str, optional
            Path to YAML specification file. Alternative to spec_dict.

        Returns
        -------
        dict
            Dictionary with 'mermaid' and 'graphviz' string representations.

        Examples
        --------
        Create a simple workflow diagram:

        >>> spec = {
        ...     "preset": "workflow",
        ...     "theme": "SCITEX",
        ...     "nodes": [
        ...         {"id": "input", "label": "Raw Data"},
        ...         {"id": "process", "label": "Analysis"},
        ...         {"id": "output", "label": "Results"}
        ...     ],
        ...     "edges": [
        ...         {"from": "input", "to": "process"},
        ...         {"from": "process", "to": "output"}
        ...     ]
        ... }
        >>> diagram_create(spec_dict=spec)
        """
        d = _load_diagram(spec_dict, spec_path)
        return {
            "mermaid": d.to_mermaid(),
            "graphviz": d.to_graphviz(),
            "nodes": len(d.spec.nodes),
            "edges": len(d.spec.edges),
            "success": True,
        }

    @mcp.tool()
    def diagram_compile_mermaid(
        spec_dict: Optional[Dict[str, Any]] = None,
        spec_path: Optional[str] = None,
        output_path: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Compile diagram specification to Mermaid format.

        Parameters
        ----------
        spec_dict : dict, optional
            Diagram specification as dictionary.

        spec_path : str, optional
            Path to YAML specification file.

        output_path : str, optional
            Path to save .mmd file. If not specified, returns the Mermaid string only.

        Returns
        -------
        dict
            Dictionary with 'mermaid' string and 'output_path' (if saved).
        """
        d = _load_diagram(spec_dict, spec_path)
        mermaid = d.to_mermaid(output_path)
        return {"mermaid": mermaid, "output_path": output_path, "success": True}

    @mcp.tool()
    def diagram_compile_graphviz(
        spec_dict: Optional[Dict[str, Any]] = None,
        spec_path: Optional[str] = None,
        output_path: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Compile diagram specification to Graphviz DOT format.

        Parameters
        ----------
        spec_dict : dict, optional
            Diagram specification as dictionary.

        spec_path : str, optional
            Path to YAML specification file.

        output_path : str, optional
            Path to save .dot file. If not specified, returns the DOT string only.

        Returns
        -------
        dict
            Dictionary with 'graphviz' string and 'output_path' (if saved).
        """
        d = _load_diagram(spec_dict, spec_path)
        graphviz = d.to_graphviz(output_path)
        return {"graphviz": graphviz, "output_path": output_path, "success": True}

    @mcp.tool()
    def diagram_render(
        spec_dict: Optional[Dict[str, Any]] = None,
        spec_path: Optional[str] = None,
        output_path: str = "",
        format: Literal["png", "svg", "pdf"] = "png",
        backend: Literal["auto", "mermaid-cli", "graphviz", "mermaid.ink"] = "auto",
        scale: float = 2.0,
    ) -> Dict[str, Any]:
        """Render diagram to image file (PNG, SVG, PDF).

        Parameters
        ----------
        spec_dict : dict, optional
            Diagram specification as dictionary.

        spec_path : str, optional
            Path to YAML specification file.

        output_path : str
            Path to save the rendered image.

        format : str
            Output format: png, svg, or pdf.

        backend : str
            Rendering backend:
            - auto: Automatically choose best available backend
            - mermaid-cli: Use mermaid-cli (requires npm install -g @mermaid-js/mermaid-cli)
            - graphviz: Use Graphviz dot command
            - mermaid.ink: Use online Mermaid.ink service (no local install required)

        scale : float
            Scale factor for rendering (default: 2.0 for high DPI).

        Returns
        -------
        dict
            Dictionary with 'output_path' and 'success' status.
        """
        if not output_path:
            raise ValueError("output_path is required")
        d = _load_diagram(spec_dict, spec_path)
        result_path = d.render(output_path, format=format, backend=backend, scale=scale)
        return {
            "output_path": str(result_path),
            "format": format,
            "backend": backend,
            "success": True,
        }

    @mcp.tool()
    def diagram_split(
        spec_path: str,
        max_nodes_per_part: int = 10,
        strategy: Literal["by_groups", "by_articulation"] = "by_groups",
    ) -> Dict[str, Any]:
        """Split a large diagram into smaller parts for multi-column layouts.

        Useful for complex diagrams that need to be broken down into
        manageable pieces for publication layouts.

        Parameters
        ----------
        spec_path : str
            Path to the YAML specification file.

        max_nodes_per_part : int
            Maximum number of nodes per split part (default: 10).

        strategy : str
            Splitting strategy:
            - by_groups: Split based on node groups defined in spec
            - by_articulation: Split at articulation points in the graph

        Returns
        -------
        dict
            Dictionary with split parts and metadata about the splitting.
        """
        d = Diagram.from_yaml(spec_path)
        parts = d.split(max_nodes=max_nodes_per_part, strategy=strategy)
        return {
            "parts": [
                {
                    "title": p.spec.title,
                    "nodes": len(p.spec.nodes),
                    "edges": len(p.spec.edges),
                    "mermaid": p.to_mermaid(),
                }
                for p in parts
            ],
            "num_parts": len(parts),
            "success": True,
        }


# EOF
