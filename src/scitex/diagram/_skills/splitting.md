---
name: diagram-splitting
description: Divide large stx.diagram diagrams into multi-figure sets for publication — SplitConfig, SplitStrategy, SplitResult, and Diagram.split with by_groups and by_articulation strategies.
---

# Diagram Splitting

Large diagrams often need to be split into multiple figures for paper columns. The splitting system produces labeled figure parts (A, B, C…) with ghost nodes at boundaries.

## Diagram.split

```python
diagram.split(max_nodes=12, strategy="by_groups", keep_hubs=True) -> list[Diagram]
```

**Parameters**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `max_nodes` | `int` | `12` | Maximum number of nodes per output part |
| `strategy` | `str` | `"by_groups"` | Split algorithm — see strategies below |
| `keep_hubs` | `bool` | `True` | Keep highly-connected hub nodes in each part they appear in |

Returns a list of `Diagram` objects, one per output figure part. Ghost nodes are automatically added at cross-part boundaries.

```python
import scitex as stx

d = stx.diagram.Diagram.from_yaml("large_workflow.diagram.yaml")
parts = d.split(max_nodes=8, strategy="by_groups")

for i, part in enumerate(parts):
    label = chr(ord("A") + i)          # A, B, C, ...
    part.to_mermaid(f"fig_{label}.mmd")
    part.to_graphviz(f"fig_{label}.dot")
```

---

## Split strategies

### by_groups (recommended)

Splits based on the `layout.groups` defined in the YAML spec. Deterministic and paper-friendly because the author explicitly defines which nodes belong together.

- Groups are assigned to parts greedily until `max_nodes` is reached.
- If a single group exceeds `max_nodes`, it is placed in its own part.
- Requires `layout.groups` to be defined in the spec.

```yaml
layout:
  groups:
    Creation:
      - python_code
      - savefig
    Bundle:
      - figz_bundle
      - spec_json
      - data_csv
      - preview
    Editing:
      - editor
      - ai_review
    Output:
      - export
```

### by_articulation

Splits at articulation points (cut vertices) in the graph. Graph-theoretic approach that finds natural break points where removing a node would disconnect the graph.

- Does not require `layout.groups`.
- Non-deterministic for symmetric graphs.
- Better for automatically generated or unstructured diagrams.

```python
parts = d.split(max_nodes=6, strategy="by_articulation")
```

---

## Ghost nodes

When a node appears in part A and is referenced by part B, a **ghost node** is automatically inserted at the boundary. Ghost nodes are visually marked with a `→` prefix in their label.

```
Part A: [python_code, savefig, figz_bundle, spec_json, data_csv]
Part B: [→ figz_bundle, editor, ai_review, export]
         ^^^^^^^^^^^^^ ghost: label is "→ .figure"
```

Ghost nodes use the same shape and emphasis as the original, so the reader can identify them. The `→` prefix conventionally means "continued from the previous figure".

Detecting ghost nodes programmatically:

```python
for node in part.spec.nodes:
    is_ghost = "→" in node.label
```

---

## SplitConfig

Configuration dataclass for splitting. Used internally; accessible for advanced use.

```python
class SplitConfig:
    max_nodes:  int           # maximum nodes per part
    strategy:   SplitStrategy # by_groups | by_articulation
    keep_hubs:  bool          # keep hub nodes in every part
```

## SplitStrategy

Enum:

```python
class SplitStrategy:
    BY_GROUPS       = "by_groups"
    BY_ARTICULATION = "by_articulation"
```

## SplitResult

Container for a single part's output:

```python
class SplitResult:
    part_index: int       # 0-based part number
    diagram:    Diagram   # the sub-diagram
    label:      str       # "A", "B", "C", ...
    ghost_ids:  list[str] # node IDs that are ghosts in this part
```

---

## Manual split (alternative)

For full control, build each part as an independent `Diagram` and share boundary nodes manually:

```python
import scitex as stx

# Part A: creation flow
part_a = stx.diagram.Diagram(type="workflow", title="Figure Creation")
part_a.add_node("python",  "Python",         shape="rounded")
part_a.add_node("savefig", "savefig()",      shape="box")
part_a.add_node("figz",    ".figure Bundle", shape="stadium", emphasis="primary")
part_a.add_edge("python",  "savefig")
part_a.add_edge("savefig", "figz")
part_a.to_mermaid("fig_A.mmd")

# Part B: editing flow — figz appears again as the entry point
part_b = stx.diagram.Diagram(type="workflow", title="Figure Editing")
part_b.add_node("figz",   ".figure Bundle", shape="stadium", emphasis="primary")
part_b.add_node("editor", "Editor",         shape="rounded", emphasis="primary")
part_b.add_node("export", "Export",         shape="stadium", emphasis="success")
part_b.add_edge("figz",   "editor")
part_b.add_edge("editor", "figz",   label="changes")
part_b.add_edge("figz",   "export")
part_b.to_mermaid("fig_B.mmd")
```

---

## Choosing max_nodes

| Figure column | Recommended max_nodes |
|--------------|----------------------|
| Double-column (half-width) | 6–8 |
| Single-column (full-width) | 10–14 |
| Full-page | 16–20 |

Diagrams with many crossing edges benefit from lower `max_nodes` since each part will be visually cleaner.
