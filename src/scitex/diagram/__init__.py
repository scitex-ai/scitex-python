#!/usr/bin/env python3
# Timestamp: 2026-01-24
# Author: ywatanabe / Claude
# File: scitex/diagram/__init__.py

"""
SciTeX Diagram - Paper-optimized diagram generation.

This module delegates entirely to figrecipe._diagram.
figrecipe is the single source of truth for diagram functionality.

Example
-------
>>> import scitex as stx
>>>
>>> # Recommended: Use stx.Diagram directly
>>> d = stx.Diagram(type="pipeline")
>>> d.add_node("input", "Raw Data")
>>> d.add_node("process", "Transform", emphasis="primary")
>>> d.add_edge("input", "process")
>>> d.to_mermaid("pipeline.mmd")
>>>
>>> # From YAML spec
>>> d = stx.Diagram.from_yaml("workflow.diagram.yaml")
>>> d.to_mermaid("workflow.mmd")
>>> d.to_graphviz("workflow.dot")
"""

# Import everything from figrecipe._diagram (single source of truth)
from figrecipe._diagram import (
    DECISION_PRESET,
    PIPELINE_PRESET,
    SCIENTIFIC_PRESET,
    WORKFLOW_PRESET,
    Diagram,
    DiagramSpec,
    DiagramType,
    EdgeSpec,
    LayoutHints,
    NodeSpec,
    PaperConstraints,
    PaperMode,
    SplitConfig,
    SplitResult,
    SplitStrategy,
    get_preset,
    list_presets,
)
from figrecipe._diagram._graphviz import compile_to_graphviz
from figrecipe._diagram._mermaid import compile_to_mermaid

__all__ = [
    "Diagram",
    "DiagramSpec",
    "DiagramType",
    "NodeSpec",
    "EdgeSpec",
    "PaperConstraints",
    "LayoutHints",
    "PaperMode",
    "compile_to_mermaid",
    "compile_to_graphviz",
    "WORKFLOW_PRESET",
    "DECISION_PRESET",
    "PIPELINE_PRESET",
    "SCIENTIFIC_PRESET",
    "get_preset",
    "list_presets",
    "SplitConfig",
    "SplitStrategy",
    "SplitResult",
]
