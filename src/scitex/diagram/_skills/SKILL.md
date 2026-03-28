---
name: stx.diagram
description: Paper-optimized diagram generation with Mermaid and Graphviz backends via figrecipe. Use for creating scientific workflow, pipeline, decision, and comparison diagrams in publication-ready layouts.
user-invocable: false
---

# stx.diagram

The `stx.diagram` module provides paper-optimized diagram generation, delegating entirely to `figrecipe._diagram`. It supports semantic diagram construction, YAML-driven specifications, dual backend compilation (Mermaid + Graphviz), paper-aware layout constraints, and automatic splitting of large diagrams.

## Sub-skills

### Construction
- [construction.md](construction.md) — `Diagram`, `add_node`, `add_edge`, `set_group`, `emphasize`: build diagrams programmatically or load from YAML/Mermaid files

### Schema
- [schema.md](schema.md) — `DiagramSpec`, `NodeSpec`, `EdgeSpec`, `DiagramType`: typed specification objects that define the semantic layer

### Paper Layout
- [paper-layout.md](paper-layout.md) — `PaperMode`, `PaperConstraints`, `LayoutHints`: single/double column, draft/publication modes, explicit layer ordering

### Backend Compilation
- [backends.md](backends.md) — `compile_to_mermaid`, `compile_to_graphviz`, `to_mermaid`, `to_graphviz`: produce `.mmd` and `.dot` output, shape/style mappings

### Presets
- [presets.md](presets.md) — `PIPELINE_PRESET`, `SCIENTIFIC_PRESET`, `WORKFLOW_PRESET`, `DECISION_PRESET`, `list_presets`, `get_preset`: ready-to-use diagram templates

### Splitting
- [splitting.md](splitting.md) — `SplitConfig`, `SplitStrategy`, `SplitResult`, `Diagram.split`: divide large diagrams into multi-figure sets for publication

### MCP Interface
- [mcp.md](mcp.md) — `plt_diagram_create`, `plt_diagram_compile_mermaid`, `plt_diagram_compile_graphviz`, `plt_diagram_render`, `plt_diagram_split`, `plt_diagram_list_presets`, `plt_diagram_get_preset`, `plt_diagram_get_backends`, `plt_diagram_get_paper_modes`
