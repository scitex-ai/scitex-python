Diagram Module (``stx.diagram``)
=================================

Paper-optimized diagram generation with Mermaid and Graphviz backends.

Quick Reference
---------------

.. code-block:: python

   from scitex.diagram import Diagram

   # Create from Python
   d = Diagram(type="workflow", title="Analysis Pipeline")
   d.add_node("load", "Load Data", shape="stadium")
   d.add_node("proc", "Process", shape="rounded", emphasis="primary")
   d.add_node("save", "Save Results", shape="stadium", emphasis="success")
   d.add_edge("load", "proc")
   d.add_edge("proc", "save")

   # Export
   d.to_mermaid("pipeline.mmd")
   d.to_graphviz("pipeline.dot")

   # Or from YAML specification
   d = Diagram.from_yaml("pipeline.diagram.yaml")

YAML Specification
------------------

.. code-block:: yaml

   type: workflow
   title: SciTeX Analysis Pipeline

   paper:
     column: single          # single or double
     mode: publication       # draft or publication
     reading_direction: left_to_right

   layout:
     groups:
       Input: [load, preprocess]
       Analysis: [analyze, test]

   nodes:
     - id: load
       label: Load Data
       shape: stadium
     - id: analyze
       label: Statistical Test
       shape: rounded
       emphasis: primary

   edges:
     - from: load
       to: analyze

Node Shapes
------------

``box``, ``rounded``, ``stadium``, ``diamond``, ``circle``, ``codeblock``

Node Emphasis
-------------

- ``normal`` -- Default (dark)
- ``primary`` -- Key nodes (blue)
- ``success`` -- Positive outcomes (green)
- ``warning`` -- Issues (red)
- ``muted`` -- Secondary (gray)

Diagram Types
-------------

- ``workflow`` -- Left-to-right sequential processes
- ``decision`` -- Top-to-bottom decision trees
- ``pipeline`` -- Data pipeline stages
- ``hierarchy`` -- Tree structures
- ``comparison`` -- Side-by-side comparison

Paper Modes
-----------

- **draft** -- Full arrows, medium spacing, all edges visible
- **publication** -- Tight spacing, return edges invisible, optimized for column width

Backends
--------

- **Mermaid** (``.mmd``) -- Web/markdown rendering
- **Graphviz DOT** (``.dot``) -- Tighter layouts, render with ``dot -Tpng``
- **YAML** (``.diagram.yaml``) -- Semantic spec, human/LLM-readable

API Reference
-------------

.. automodule:: scitex.diagram
   :members:
