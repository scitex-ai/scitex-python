---
name: diagram-backends
description: Backend compilation for stx.diagram — compile_to_mermaid and compile_to_graphviz module-level functions, to_mermaid/to_graphviz instance methods, shape/style mappings, and rendering with mmdc/dot.
---

# Backend Compilation

`stx.diagram` compiles the semantic spec to two backends: **Mermaid** (`.mmd`) and **Graphviz** (`.dot`). Both backends are accessible as module-level functions and as instance methods on `Diagram`.

---

## Module-level functions

### compile_to_mermaid

```python
compile_to_mermaid(spec: DiagramSpec) -> str
```

Compiles a `DiagramSpec` to a Mermaid flowchart string. Returns the full `.mmd` text.

```python
from scitex.diagram import compile_to_mermaid, DiagramSpec

mmd_text = compile_to_mermaid(diagram.spec)
```

### compile_to_graphviz

```python
compile_to_graphviz(spec: DiagramSpec) -> str
```

Compiles a `DiagramSpec` to a Graphviz DOT string. Returns the full `.dot` text.

```python
from scitex.diagram import compile_to_graphviz

dot_text = compile_to_graphviz(diagram.spec)
```

---

## Instance methods

```python
diagram.to_mermaid(path=None) -> str
diagram.to_graphviz(path=None) -> str
```

Both methods compile the diagram's `spec` using the corresponding module-level function.

- If `path` is provided the result is written to disk and the string is still returned.
- If `path` is `None` the string is returned only.

---

## Mermaid output format

The compiler emits a Mermaid `graph LR` (or `graph TB` for decision/hierarchy types) with:

- A theme `init` directive at the top:
  - **Dark theme** (default when `PaperMode.PUBLICATION`): `primaryColor: "#1a2634"`, blue emphasis nodes
  - **Light theme** (when `PaperMode.DRAFT`): `primaryColor: "#f5f5f5"`, lighter emphasis nodes
- Subgraph blocks for each group defined via `set_group` / `layout.groups`
- Node syntax per shape:

| Shape | Mermaid syntax |
|-------|---------------|
| `"box"` | `id["label"]` |
| `"rounded"` | `id("label")` |
| `"stadium"` | `id(["label"])` |
| `"diamond"` | `id{"label"}` |
| `"circle"` | `id(("label"))` |

- Edge syntax:

| Style | Mermaid |
|-------|---------|
| `"solid"` without label | `a --> b` |
| `"solid"` with label | `a -->|"label"| b` |
| `"dashed"` without label | `a -.-> b` |

- `style` directives appended at the end for non-normal emphasis nodes.

**Example output** (pipeline, double-column, publication mode):

```
%%{init: {"theme": "base", "themeVariables": {"primaryColor": "#1a2634", ...}}}%%
graph LR
    subgraph Processing["Processing"]
        clean["Preprocessing"]
        transform["Feature Extraction"]
    end
    subgraph Analysis["Analysis"]
        model["ML Model"]
    end
    input(["Raw Data"])
    output(["Results"])
    input --> clean
    clean --> transform
    transform --> model
    model --> output
    style transform fill:#0d4a6b,stroke:#5a9fcf,stroke-width:2px
    style model fill:#0d4a6b,stroke:#5a9fcf,stroke-width:2px
```

---

## Graphviz DOT output format

The compiler emits a `digraph G { ... }` with:

| DOT attribute | Draft value | Publication value |
|--------------|-------------|-------------------|
| `rankdir` | `LR` | `LR` |
| `ranksep` | `0.5` | `0.3` |
| `nodesep` | `0.4` | `0.2` |
| `splines` | `ortho` | `ortho` |

Node attributes:

| Shape | DOT shape | Additional |
|-------|-----------|-----------|
| `"box"` | `shape=box` | — |
| `"rounded"` | `shape=box` | `style=rounded` |
| `"stadium"` | `shape=box` | — |
| `"diamond"` | `shape=diamond` | — |

Emphasis fills:

| Emphasis | `fillcolor` |
|----------|-------------|
| `"normal"` | `#1a2634` (dark) |
| `"primary"` | `#0d4a6b` (blue) |
| `"success"` | `#ccffcc` (green) |
| `"warning"` | `#ffcccc` (red) |
| `"muted"` | `#f0f0f0` (gray) |

`style=filled` is added to all nodes. In publication mode, `return_edges` are emitted as:

```dot
editor -> figz_bundle [style=invis, constraint=true];
```

`rank=same` blocks are emitted for each entry in `layout.layers`:

```dot
{ rank=same; python_code; savefig; }
{ rank=same; figz_bundle; }
```

**Example output** (publication mode, 9 nodes):

```dot
digraph G {
    rankdir=LR;
    ranksep=0.3;
    nodesep=0.2;
    splines=ortho;
    node [fontname="Helvetica", fontsize=10];
    edge [fontname="Helvetica", fontsize=9];

    python_code [label="Python", shape=box, fillcolor="#1a2634", style=filled, ...];
    figz_bundle [label=".figure", shape=box, fillcolor="#0d4a6b", style=filled, ...];
    ...

    { rank=same; python_code; savefig; }
    { rank=same; figz_bundle; }

    python_code -> savefig;
    editor -> figz_bundle [style=invis, constraint=true];
}
```

---

## Rendering to image

Mermaid requires the `mmdc` CLI (`@mermaid-js/mermaid-cli`):

```bash
# PNG (transparent background, 800px wide)
mmdc -i workflow.mmd -o workflow.png -b transparent -w 800

# SVG (vector, best for papers)
mmdc -i workflow.mmd -o workflow.svg
```

Graphviz requires the `dot` binary:

```bash
# PNG
dot -Tpng workflow.dot -o workflow.png

# SVG (tightest layout, recommended for publication)
dot -Tsvg workflow.dot -o workflow.svg

# PDF
dot -Tpdf workflow.dot -o workflow.pdf
```

**Why Graphviz for publication**: Mermaid does not support `rank=same` constraints, so Graphviz produces more compact, predictable layouts in publication mode. Use Mermaid for quick drafts and review; use Graphviz for the final figure.

---

## Choosing the backend

| Criteria | Use Mermaid | Use Graphviz |
|----------|------------|--------------|
| Quick preview | Yes | — |
| GitHub/Notion rendering | Yes | — |
| Strict rank constraints | No | Yes |
| Compact publication layout | No | Yes |
| Custom spline routing | No | Yes (`splines=ortho`) |
| `mmdc` available | Required | Not needed |
| `dot` available | Not needed | Required |
