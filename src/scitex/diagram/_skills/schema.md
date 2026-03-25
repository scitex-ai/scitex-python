---
name: diagram-schema
description: Typed specification objects that form the semantic layer of stx.diagram — DiagramSpec, NodeSpec, EdgeSpec, DiagramType, and related enums.
---

# Diagram Schema

The semantic layer is a set of dataclass-like objects that describe *what a diagram means*, independent of the backend that renders it. The `Diagram` class wraps a `DiagramSpec` internally; `Diagram.spec` gives direct access.

## DiagramSpec

The root specification object. Contains all information needed to compile to any backend.

```python
class DiagramSpec:
    type:   DiagramType          # diagram kind
    title:  str                  # human-readable title
    nodes:  list[NodeSpec]
    edges:  list[EdgeSpec]
    paper:  PaperConstraints     # see paper-layout.md
    layout: LayoutHints          # see paper-layout.md
```

Access via `diagram.spec`. Mutate fields directly to adjust the spec before compilation:

```python
d = stx.diagram.Diagram.from_yaml("workflow.diagram.yaml")
d.spec.paper.mode = stx.diagram.PaperMode.PUBLICATION
d.spec.title = "Updated Title"
mmd = d.to_mermaid()
```

Serialize to YAML:

```python
yaml_text = d.to_yaml("spec.diagram.yaml")
```

---

## DiagramType

String enum for the diagram kind. Controls default flow direction and available layout strategies.

| Value | Direction | Use case |
|-------|-----------|----------|
| `"workflow"` | LR | Sequential processes, lifecycle |
| `"pipeline"` | LR | Data pipelines with named stages |
| `"decision"` | TB | Decision trees, branching logic |
| `"hierarchy"` | TB | Tree structures, taxonomies |
| `"comparison"` | LR | Side-by-side A vs B layouts |

```python
import scitex as stx

d = stx.diagram.Diagram(type="decision")
# equivalent to:
# d.spec.type == DiagramType.DECISION
```

---

## NodeSpec

Defines a single node.

```python
class NodeSpec:
    id:       str                # unique identifier used in EdgeSpec references
    label:    str                # display text
    shape:    str = "box"        # "box" | "rounded" | "stadium" | "diamond" | "circle" | "codeblock"
    emphasis: str = "normal"     # "normal" | "primary" | "success" | "warning" | "muted"
```

Nodes are ordered in `DiagramSpec.nodes`. The order determines insertion order in Mermaid output; layout position is determined by edges and `LayoutHints.layers`.

**Direct construction**

```python
from scitex.diagram import NodeSpec

n = NodeSpec(id="step1", label="Load Data", shape="rounded", emphasis="primary")
```

---

## EdgeSpec

Defines a directed edge between two nodes.

```python
class EdgeSpec:
    source: str          # node id (called "from" in YAML)
    target: str          # node id (called "to" in YAML)
    label:  str | None   # optional arrow label
    style:  str = "solid"  # "solid" | "dashed"
```

Note: in YAML the fields are named `from` and `to` (Python reserved word `from` is handled by the parser). In Python code, use `source` and `target`.

**YAML form**

```yaml
edges:
  - from: python_code
    to: savefig
  - from: figz_bundle
    to: data_csv
    style: dashed
  - from: editor
    to: figz_bundle
    label: changes
```

**Dashed edges** compile to `-.->` in Mermaid and `style=dashed` in Graphviz DOT. They conventionally indicate "derived from" or "optional" relationships.

---

## YAML field name mapping

The YAML format uses `from`/`to` while the Python dataclass uses `source`/`target`. The loader handles this transparently.

| YAML key | Python attribute |
|----------|-----------------|
| `from` | `EdgeSpec.source` |
| `to` | `EdgeSpec.target` |
| `label` | `EdgeSpec.label` |
| `style` | `EdgeSpec.style` |

---

## Complete YAML schema reference

```yaml
type: workflow           # DiagramType value
title: My Diagram        # str

paper:                   # PaperConstraints — see paper-layout.md
  column: single
  mode: publication
  emphasize: [node_a, node_b]
  return_edges:
    - [node_a, node_b]

layout:                  # LayoutHints — see paper-layout.md
  layer_gap: tight
  node_gap: medium
  layers:
    - [node_a, node_b]
  groups:
    GroupName:
      - node_a
      - node_b

nodes:
  - id: node_a
    label: Node A
    shape: rounded
    emphasis: primary
  - id: node_b
    label: Node B
    shape: stadium
    emphasis: success

edges:
  - from: node_a
    to: node_b
    label: transforms
    style: solid
```
