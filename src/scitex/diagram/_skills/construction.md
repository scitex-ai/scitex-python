---
description: Build diagrams programmatically using Diagram, add_node, add_edge, set_group, emphasize, or load existing diagrams from YAML specs or Mermaid files.
---

# Diagram Construction

## Diagram class

The primary entry point. Creates an empty diagram of a given type and title, then nodes and edges are added imperatively.

```python
Diagram(type="workflow", title="", column="single")
```

**Parameters**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `type` | `str` | `"workflow"` | One of `"workflow"`, `"pipeline"`, `"decision"`, `"hierarchy"`, `"comparison"` |
| `title` | `str` | `""` | Human-readable title (used in output headers) |
| `column` | `str` | `"single"` | Initial paper column hint: `"single"` (full-width) or `"double"` (half-width) |

---

## add_node

```python
diagram.add_node(id, label, shape="box", emphasis="normal")
```

**Parameters**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `id` | `str` | required | Unique node identifier (used in edge references) |
| `label` | `str` | required | Display text inside the node |
| `shape` | `str` | `"box"` | Visual shape — see shape table below |
| `emphasis` | `str` | `"normal"` | Color emphasis level — see emphasis table below |

**Shape values**

| Shape | Mermaid syntax | Use case |
|-------|---------------|----------|
| `"box"` | `["label"]` | Default, generic step |
| `"rounded"` | `("label")` | Processes, actions |
| `"stadium"` | `(["label"])` | Start/end terminals |
| `"diamond"` | `{"label"}` | Decision points |
| `"circle"` | `(("label"))` | Events |
| `"codeblock"` | `["label"]` with code style | Scripts, commands |

In Graphviz output `"rounded"` becomes `shape=box, style=rounded`; `"diamond"` becomes `shape=diamond`; all others become `shape=box`.

**Emphasis values and rendered colors**

| Emphasis | Dark-theme fill | Light-theme fill | Use case |
|----------|----------------|-----------------|----------|
| `"normal"` | `#1a2634` | `#f5f5f5` | Default |
| `"primary"` | `#0d4a6b` / blue | `#e6f3ff` | Key nodes |
| `"success"` | `#ccffcc` / green | `#e6ffe6` | Positive outcome |
| `"warning"` | `#ffcccc` / red | `#ffe6e6` | Negative/error |
| `"muted"` | `#f0f0f0` / gray | `#f0f0f0` | Secondary/derived |

---

## add_edge

```python
diagram.add_edge(source, target, label=None, style="solid")
```

**Parameters**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `source` | `str` | required | ID of the source node |
| `target` | `str` | required | ID of the target node |
| `label` | `str` | `None` | Optional text shown on the arrow |
| `style` | `str` | `"solid"` | `"solid"` → `-->` / `->`, `"dashed"` → `-.->` / `style=dashed` |

---

## set_group

Groups nodes into a named subgraph (Mermaid `subgraph`, Graphviz `cluster`).

```python
diagram.set_group(group_name, node_ids)
```

**Parameters**

| Parameter | Type | Description |
|-----------|------|-------------|
| `group_name` | `str` | Display name of the group/subgraph |
| `node_ids` | `list[str]` | List of node IDs to include in the group |

Groups can be called multiple times to build up group membership. In publication mode Graphviz uses `rank=same` instead of `cluster` to avoid boxes.

---

## emphasize

Applies `"primary"` emphasis to one or more existing nodes by ID.

```python
diagram.emphasize(*node_ids)
```

**Example** — add emphasis to nodes after construction:

```python
diagram.emphasize("model", "output")
```

This overwrites the `emphasis` field on each named node with `"primary"`.

---

## Loading from YAML

```python
Diagram.from_yaml(path) -> Diagram
```

Reads a `.diagram.yaml` file and returns a fully populated `Diagram`. The YAML structure mirrors `DiagramSpec` — see [schema.md](schema.md) and [paper-layout.md](paper-layout.md) for the full field reference.

**Minimal YAML example**

```yaml
type: workflow
title: Data Pipeline

paper:
  column: single

nodes:
  - id: input
    label: Raw Data
    shape: stadium
  - id: process
    label: Transform
    emphasis: primary
  - id: output
    label: Results
    shape: stadium

edges:
  - from: input
    to: process
  - from: process
    to: output
```

```python
import scitex as stx

d = stx.diagram.Diagram.from_yaml("pipeline.diagram.yaml")
d.to_mermaid("pipeline.mmd")
```

---

## Loading from existing Mermaid

```python
Diagram.from_mermaid(path, diagram_type="workflow") -> Diagram
```

Parses an existing `.mmd` file into the semantic layer. Node labels, shapes, and edges are extracted. Paper constraints default to empty and must be added manually after loading.

```python
d = stx.diagram.Diagram.from_mermaid("existing.mmd", diagram_type="comparison")
d.emphasize("key_node")
d.to_mermaid("enhanced.mmd")
```

---

## Export methods

```python
diagram.to_mermaid(path=None) -> str      # Returns Mermaid string; writes file if path given
diagram.to_graphviz(path=None) -> str     # Returns DOT string; writes file if path given
diagram.to_yaml(path=None) -> str         # Returns YAML string; writes file if path given
```

All three methods return the generated text as a string regardless of whether `path` is given.

---

## Full programmatic example

```python
import scitex as stx

# Build
d = stx.diagram.Diagram(type="pipeline", title="ML Pipeline")
d.add_node("input",     "Raw Data",          shape="stadium")
d.add_node("clean",     "Preprocessing")
d.add_node("transform", "Feature Extraction", emphasis="primary")
d.add_node("model",     "ML Model",           emphasis="primary")
d.add_node("output",    "Results",            shape="stadium", emphasis="success")

d.add_edge("input",     "clean")
d.add_edge("clean",     "transform")
d.add_edge("transform", "model")
d.add_edge("model",     "output")

d.set_group("Processing", ["clean", "transform"])

d.spec.paper.column = "double"

# Export
mmd = d.to_mermaid("pipeline.mmd")
dot = d.to_graphviz("pipeline.dot")
```
