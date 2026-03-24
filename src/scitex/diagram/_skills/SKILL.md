---
name: stx.diagram
description: Paper-optimized diagram generation with Mermaid and Graphviz backends via figrecipe.
---

# stx.diagram

The `stx.diagram` module provides paper-optimized diagram generation, delegating entirely to `figrecipe._diagram`. It supports pipeline, workflow, scientific, and decision diagram types with both Mermaid and Graphviz output backends.

## Python API

```python
import scitex as stx

# Create a pipeline diagram
d = stx.diagram.Diagram(type="pipeline")
d.add_node("input", "Raw Data")
d.add_node("process", "Transform", emphasis="primary")
d.add_node("output", "Results")
d.add_edge("input", "process")
d.add_edge("process", "output")

# Export to Mermaid or Graphviz
d.to_mermaid("pipeline.mmd")
d.to_graphviz("pipeline.dot")

# From YAML specification
d = stx.diagram.Diagram.from_yaml("workflow.diagram.yaml")

# Use built-in presets
presets = stx.diagram.list_presets()
d = stx.diagram.get_preset("scientific")

# Compile to different formats
mermaid_code = stx.diagram.compile_to_mermaid(diagram_spec)
graphviz_code = stx.diagram.compile_to_graphviz(diagram_spec)

# Available presets
stx.diagram.PIPELINE_PRESET
stx.diagram.SCIENTIFIC_PRESET
stx.diagram.WORKFLOW_PRESET
stx.diagram.DECISION_PRESET
```

## Key Features

- `Diagram` — main class for programmatic diagram construction
- `DiagramSpec` — declarative specification for diagrams
- `NodeSpec` / `EdgeSpec` — typed node and edge definitions
- `PaperMode` / `PaperConstraints` — paper-size-aware layout constraints
- Built-in presets: `PIPELINE_PRESET`, `SCIENTIFIC_PRESET`, `WORKFLOW_PRESET`, `DECISION_PRESET`
- `compile_to_mermaid` / `compile_to_graphviz` — backend compilation
- `SplitConfig` / `SplitResult` — multi-page diagram splitting
