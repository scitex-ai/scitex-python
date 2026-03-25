---
description: MCP tool interface for stx.diagram — plt_diagram_create, compile_mermaid, compile_graphviz, render, split, list_presets, get_preset, get_backends, get_paper_modes.
---

# MCP Interface

All diagram MCP tools are prefixed `plt_diagram_`. They accept either a `spec_dict` (inline Python dict) or a `spec_path` (path to a `.diagram.yaml` file).

---

## plt_diagram_create

Create a diagram from a spec and return both Mermaid and Graphviz output in one call.

```
plt_diagram_create(spec_dict=None, spec_path=None)
```

| Parameter | Type | Description |
|-----------|------|-------------|
| `spec_dict` | `dict \| null` | Inline diagram spec as a dict |
| `spec_path` | `str \| null` | Path to a `.diagram.yaml` file |

Returns `{"mermaid": "<mmd text>", "graphviz": "<dot text>"}`.

**Example**

```json
{
  "spec_dict": {
    "type": "pipeline",
    "title": "My Pipeline",
    "nodes": [
      {"id": "input",  "label": "Raw Data",  "shape": "stadium"},
      {"id": "proc",   "label": "Transform", "emphasis": "primary"},
      {"id": "output", "label": "Results",   "shape": "stadium"}
    ],
    "edges": [
      {"from": "input", "to": "proc"},
      {"from": "proc",  "to": "output"}
    ]
  }
}
```

---

## plt_diagram_compile_mermaid

Compile a spec to Mermaid only, with optional file write.

```
plt_diagram_compile_mermaid(spec_dict=None, spec_path=None, output_path=None)
```

| Parameter | Type | Description |
|-----------|------|-------------|
| `spec_dict` | `dict \| null` | Inline spec |
| `spec_path` | `str \| null` | Path to YAML spec |
| `output_path` | `str \| null` | Path to save `.mmd` file |

Returns `{"mermaid": "<mmd text>", "output_path": "<path or null>"}`.

---

## plt_diagram_compile_graphviz

Compile a spec to Graphviz DOT only, with optional file write.

```
plt_diagram_compile_graphviz(spec_dict=None, spec_path=None, output_path=None)
```

| Parameter | Type | Description |
|-----------|------|-------------|
| `spec_dict` | `dict \| null` | Inline spec |
| `spec_path` | `str \| null` | Path to YAML spec |
| `output_path` | `str \| null` | Path to save `.dot` file |

Returns `{"graphviz": "<dot text>", "output_path": "<path or null>"}`.

---

## plt_diagram_render

Render a diagram spec directly to an image file (PNG, SVG, or PDF).

```
plt_diagram_render(
    spec_dict=None,
    spec_path=None,
    output_path="",
    format="png",
    backend="auto",
    scale=2.0
)
```

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `spec_dict` | `dict \| null` | `null` | Inline spec |
| `spec_path` | `str \| null` | `null` | Path to YAML spec |
| `output_path` | `str` | `""` | Path to write the image file |
| `format` | `str` | `"png"` | `"png"` \| `"svg"` \| `"pdf"` |
| `backend` | `str` | `"auto"` | `"mermaid-cli"` \| `"graphviz"` \| `"mermaid.ink"` \| `"auto"` |
| `scale` | `float` | `2.0` | Scale factor (for Mermaid CLI raster output) |

Returns `{"output_path": "<path>", "success": true|false}`.

`"auto"` backend selects `mermaid-cli` if `mmdc` is installed, otherwise falls back to `graphviz` if `dot` is installed, otherwise `mermaid.ink` (cloud).

---

## plt_diagram_split

Split a large YAML spec into multiple figure parts.

```
plt_diagram_split(
    spec_path,
    max_nodes_per_part=10,
    strategy="by_groups"
)
```

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `spec_path` | `str` | required | Path to `.diagram.yaml` file |
| `max_nodes_per_part` | `int` | `10` | Maximum nodes per output part |
| `strategy` | `str` | `"by_groups"` | `"by_groups"` \| `"by_articulation"` |

Returns a dict with the split diagram parts (Mermaid + Graphviz text for each part).

---

## plt_diagram_list_presets

List all available built-in presets.

```
plt_diagram_list_presets()
```

No parameters. Returns `{"presets": {"<name>": "<description>", ...}}`.

---

## plt_diagram_get_preset

Get the full configuration of a named preset.

```
plt_diagram_get_preset(preset_name)
```

| Parameter | Type | Description |
|-----------|------|-------------|
| `preset_name` | `str` | One of `"workflow"`, `"decision"`, `"pipeline"`, `"scientific"` |

Returns the preset configuration dict including Mermaid and Graphviz settings.

---

## plt_diagram_get_backends

List available rendering backends and their installation status.

```
plt_diagram_get_backends()
```

No parameters. Returns backend availability, install instructions, and supported formats.

---

## plt_diagram_get_paper_modes

Get all paper layout modes and their constraints.

```
plt_diagram_get_paper_modes()
```

No parameters. Returns paper modes with width constraints.

---

## Workflow example via MCP

**Step 1** — check which backends are available:

```
plt_diagram_get_backends()
```

**Step 2** — create and compile from an inline spec:

```json
plt_diagram_create({
  "spec_dict": {
    "type": "workflow",
    "title": "Analysis Pipeline",
    "paper": {"column": "single", "mode": "publication"},
    "nodes": [
      {"id": "data",    "label": "Input Data",  "shape": "stadium"},
      {"id": "analyze", "label": "Analyze",     "emphasis": "primary"},
      {"id": "report",  "label": "Report",      "shape": "stadium", "emphasis": "success"}
    ],
    "edges": [
      {"from": "data",    "to": "analyze"},
      {"from": "analyze", "to": "report"}
    ]
  }
})
```

**Step 3** — render to PNG:

```json
plt_diagram_render({
  "spec_path": "analysis.diagram.yaml",
  "output_path": "analysis.png",
  "format": "png",
  "backend": "graphviz",
  "scale": 2.0
})
```
