---
description: Built-in diagram templates in stx.diagram — PIPELINE_PRESET, SCIENTIFIC_PRESET, WORKFLOW_PRESET, DECISION_PRESET, and the list_presets / get_preset API.
---

# Presets

Built-in diagram templates provide ready-to-use starting points. Each preset is a `DiagramSpec` object with sensible defaults for a common diagram pattern.

## Available presets

| Name | Type | Direction | Use case |
|------|------|-----------|---------|
| `"workflow"` | `workflow` | LR | Sequential lifecycle diagrams |
| `"pipeline"` | `pipeline` | LR | Data pipeline with named stages |
| `"decision"` | `decision` | TB | Decision trees, flowcharts |
| `"scientific"` | `workflow` | LR | Scientific analysis workflows |

## list_presets

```python
list_presets() -> list[str]
```

Returns a list of available preset names.

```python
import scitex as stx

names = stx.diagram.list_presets()
# e.g. ["workflow", "decision", "pipeline", "scientific"]
```

## get_preset

```python
get_preset(name: str) -> Diagram
```

Returns a `Diagram` instance pre-populated with the named preset spec. The returned diagram can be modified before export.

```python
import scitex as stx

d = stx.diagram.get_preset("pipeline")
# Modify nodes/edges as needed
d.add_node("custom", "My Step", emphasis="primary")
d.to_mermaid("my_pipeline.mmd")
```

## Module-level preset constants

The four presets are also importable as module-level constants. These are `DiagramSpec` objects, not `Diagram` instances.

```python
from scitex.diagram import (
    PIPELINE_PRESET,
    SCIENTIFIC_PRESET,
    WORKFLOW_PRESET,
    DECISION_PRESET,
)

# Use with compile functions directly
from scitex.diagram import compile_to_mermaid

mmd = compile_to_mermaid(WORKFLOW_PRESET)
```

## Using a preset as a starting template

```python
import scitex as stx

# Get preset as a mutable Diagram
d = stx.diagram.get_preset("scientific")

# Inspect what nodes/edges it comes with
for node in d.spec.nodes:
    print(node.id, node.label, node.emphasis)

# Override title and add paper constraints
d.spec.title = "My Analysis Workflow"
d.spec.paper.mode = stx.diagram.PaperMode.PUBLICATION
d.spec.paper.column = "single"

# Export
d.to_mermaid("analysis.mmd")
d.to_graphviz("analysis.dot")
```

## Relationship to Diagram constructor

`get_preset("pipeline")` is equivalent to loading the `PIPELINE_PRESET` spec into a new `Diagram`. The `Diagram(type="pipeline")` constructor creates an *empty* diagram of that type — it does not include preset nodes or edges.

| Method | Includes preset nodes/edges | Empty |
|--------|----------------------------|-------|
| `Diagram(type="pipeline")` | No | Yes (blank canvas) |
| `get_preset("pipeline")` | Yes | No (populated) |
