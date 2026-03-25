---
name: diagram-paper-layout
description: Paper-aware layout system for stx.diagram — PaperMode (draft vs publication), PaperConstraints (column, emphasize, return_edges), LayoutHints (layers, groups, spacing).
---

# Paper Layout

The semantic layer encodes paper constraints separately from content. This lets the same diagram spec compile differently for a draft review versus a publication figure.

## PaperMode

Enum with two values:

| Value | Graphviz spacings | Return edges | Clusters |
|-------|------------------|--------------|---------|
| `"draft"` | `ranksep=0.5`, `nodesep=0.4` | Visible with labels | Subgraph clusters shown |
| `"publication"` | `ranksep=0.3`, `nodesep=0.2` | Invisible (`style=invis`, `constraint=true`) | No clusters; `rank=same` only |

Set in Python:

```python
from scitex.diagram import PaperMode

diagram.spec.paper.mode = PaperMode.PUBLICATION
# or
diagram.spec.paper.mode = PaperMode.DRAFT
```

Set in YAML:

```yaml
paper:
  mode: publication   # or: draft
```

**Publication mode** is the right choice for journal figures: it eliminates whitespace waste and hides feedback loops (return edges) while still using them as invisible constraints so Graphviz respects the intended rank structure.

---

## PaperConstraints

All paper-related settings live on `diagram.spec.paper`.

```python
class PaperConstraints:
    column:            str        # "single" | "double"
    max_width_mm:      float      # e.g. 170 for single-column A4
    reading_direction: str        # "left_to_right" | "top_to_bottom"
    mode:              PaperMode  # draft | publication
    emphasize:         list[str]  # node IDs to receive "primary" emphasis at compile time
    return_edges:      list[list[str]]  # [[src, tgt], ...] — hidden in publication mode
```

### column

Controls flow direction in Mermaid:

| Column | Mermaid direction | Graphviz `rankdir` |
|--------|------------------|--------------------|
| `"single"` | `graph LR` | `LR` |
| `"double"` | `graph LR` | `LR` |

Both currently produce `LR`. The distinction is reserved for downstream width-capping logic (e.g. `max_width_mm: 85` for a half-column figure).

### max_width_mm

Hint for external renderers. Standard values:

| Layout | `max_width_mm` |
|--------|---------------|
| Single column (full-width) | `170` |
| Double column (half-width) | `85` |

### reading_direction

| Value | Mermaid | Graphviz |
|-------|---------|----------|
| `"left_to_right"` | `graph LR` | `rankdir=LR` |
| `"top_to_bottom"` | `graph TB` | `rankdir=TB` |

Decision trees (`type: decision`) default to `"top_to_bottom"`.

### emphasize

List of node IDs to programmatically mark as `emphasis="primary"` at compile time, without editing individual `NodeSpec` objects. Useful when loading a generic YAML and wanting to highlight specific nodes contextually.

```yaml
paper:
  emphasize:
    - figz_bundle
    - editor
    - ai_review
```

### return_edges

In workflows with feedback loops (e.g. editor → bundle → editor), the return edge can clutter a publication figure. Listing it in `return_edges` causes the compiler to emit `style=invis, constraint=true` in Graphviz — the edge constrains layout rank but is not drawn.

```yaml
paper:
  mode: publication
  return_edges:
    - [editor, figz_bundle]
    - [ai_review, figz_bundle]
```

The same edges are visible in draft mode regardless of this list.

---

## LayoutHints

Controls spacing and explicit rank assignment.

```python
class LayoutHints:
    layer_gap: str          # "tight" | "medium" | "large"
    node_gap:  str          # "tight" | "medium" | "large"
    layers:    list[list[str]]   # explicit rank=same groups
    groups:    dict[str, list[str]]  # named subgraphs
```

### layer_gap / node_gap

| Value | Graphviz `ranksep` | Graphviz `nodesep` |
|-------|-------------------|-------------------|
| `"tight"` | overridden by `PaperMode` | overridden by `PaperMode` |
| `"medium"` | `0.5` | `0.4` |
| `"large"` | `0.8` | `0.6` |

In `publication` mode the `PaperMode` spacings always win.

### layers

Explicit `rank=same` assignments for Graphviz. Each inner list becomes one `{ rank=same; ... }` block. Mermaid does not support `rank=same` — layers are silently ignored for Mermaid output.

```yaml
layout:
  layers:
    - [python_code, savefig]       # Layer 1: rendered at the same rank
    - [figz_bundle]                 # Layer 2
    - [spec_json, data_csv, preview] # Layer 3
    - [editor, ai_review]           # Layer 4
    - [export]                      # Layer 5
```

This produces compact, deterministic layouts regardless of edge order.

### groups

Named subgraph membership. In Mermaid these become `subgraph` blocks. In Graphviz draft mode they become `subgraph cluster_*` blocks. In Graphviz publication mode they are converted to `rank=same` to eliminate cluster whitespace.

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
```

Programmatic equivalent:

```python
diagram.set_group("Creation", ["python_code", "savefig"])
diagram.set_group("Bundle", ["figz_bundle", "spec_json", "data_csv"])
```

---

## Full publication spec example

This is the actual YAML used by the SciTeX figure lifecycle diagram:

```yaml
type: workflow
title: SciTeX Figure Lifecycle

paper:
  column: single
  max_width_mm: 170
  reading_direction: left_to_right
  mode: publication
  emphasize:
    - figz_bundle
    - editor
    - ai_review
  return_edges:
    - [editor, figz_bundle]
    - [ai_review, figz_bundle]

layout:
  layer_gap: tight
  node_gap: tight
  layers:
    - [python_code, savefig]
    - [figz_bundle]
    - [spec_json, data_csv, preview]
    - [editor, ai_review]
    - [export]
```

And the corresponding Graphviz DOT output (actual rendered output):

```dot
digraph G {
    rankdir=LR;
    ranksep=0.3;
    nodesep=0.2;
    splines=ortho;
    node [fontname="Helvetica", fontsize=10];

    { rank=same; python_code; savefig; }
    { rank=same; figz_bundle; }
    { rank=same; spec_json; data_csv; preview; }
    { rank=same; editor; ai_review; }
    { rank=same; export; }

    editor -> figz_bundle [style=invis, constraint=true];
    ai_review -> figz_bundle [style=invis, constraint=true];
    ...
}
```
