<!-- ---
!-- Timestamp: 2025-12-19
!-- Author: ywatanabe
!-- File: /home/ywatanabe/proj/scitex-python/examples/fig/README.md
!-- --- -->

# scitex.fig Examples

**Examples demonstrating the `.zip` bundle format and Figz API**

---

## Quick Start

```bash
cd /path/to/scitex-python
./examples/fig/01_basic_figure.py
```

---

## Available Examples

### 01. Basic Figure Creation
`01_basic_figure.py` - Create your first figure bundle

- Creating a `Figz` figure bundle
- Setting figure size in millimeters
- Understanding the output bundle structure

### 02. Adding Plot Panels
`02_adding_plots.py` - Multi-panel figure with matplotlib plots

- Adding matplotlib figures as elements
- Using `scitex.dev.plt` plotters (line, scatter, bar, box)
- Positioning plots in a grid layout

### 03. Text and Shape Elements
`03_text_and_shapes.py` - Annotations and decorations

- Text elements (titles, labels)
- Shape elements (arrows, brackets)
- Symbol elements (star, dagger)
- Equation elements (LaTeX math)

### 04. Panel Labels
`04_panel_labels.py` - Scientific figure labeling

- Manual panel letter assignment (`set_panel_info`)
- Auto-assign panel letters (`auto_assign_panel_letters`)
- Label styles: uppercase, lowercase, roman, Roman

### 05. Caption Generation
`05_caption_generation.py` - Auto-generated figure captions

- Setting figure title with number
- Panel descriptions for captions
- Export formats: plain text, LaTeX, Markdown

### 06. Bundle Structure
`06_bundle_structure.py` - Understanding `.zip` internals

- Canonical files: spec.json, encoding.json, theme.json
- Cache files: geometry_px.json, hitmap
- Export files: PNG, SVG, PDF

### 08. Hit-Testing Demo
`08_hittest_demo.py` - Interactive hit-testing proof

- geometry_px.json + hitmap work together
- Mapping pixel coordinates to element IDs
- Hit detection stability across cache regeneration

### 10. Theme Inheritance
`10_theme_inheritance.py` - Recursive theme inheritance

- Figure theme applies to all child plots
- Child plots can override specific fields
- Resolved theme = parent merged with child overrides

### 11. Stats Annotation Binding
`11_stats_annotation_binding.py` - Stats-driven annotations

- stats/stats.json drives visual annotations
- result_id links statistical results to visual elements
- Significance stars (*, **, ***) derived from p-value

### 07. Round-Trip Edit
`07_roundtrip_edit.py` - Canonical vs cache separation

- Edit theme.json without touching data/spec
- Delete cache/exports, re-render
- Verify deterministic regeneration

### 09. Data Swap Same Encoding
`09_data_swap_same_encoding.py` - Reusable encoding

- Same encoding.json, different data.csv
- Plots update correctly with new data
- Y-range changes automatically

### 12. Export Profiles
`12_export_profiles.py` - Journal presets (Nature, Cell, IEEE)

- Same canonical plot, multiple export styles
- Profile-specific fonts, DPI, linewidths
- Data unchanged across profiles

### 13. Layout Edit
`13_layout_edit_bbox_norm.py` - Canonical geometry editing

- spec.json positions (mm) are source of truth
- geometry_px.json (px) is derived
- Edit canonical → delete cache → re-render

### 14. ZIP Portability
`14_zip_portability.py` - Single-file portability

- .zip.d (directory) ↔ .zip (ZIP) round-trip
- Pack, delete directory, load from ZIP
- Both formats fully interchangeable

### 15. Backward Compatibility
`15_style_bridge.py` - Legacy style.json support

- Old bundles with style.json still work
- Loader creates encoding.json + theme.json
- Gradual migration, no breaking changes

---

## Pattern: scitex.session

All examples use the `@stx.session` decorator pattern:

```python
import scitex as stx
from scitex import INJECTED
from scitex.canvas import Figz

@stx.session(verbose=False, agg=True)
def main(plt=INJECTED, CONFIG=INJECTED, logger=INJECTED):
    out_dir = CONFIG["SDIR_OUT"]

    fig = Figz(
        out_dir / "my_figure.zip.d",
        name="My Figure",
        size_mm={"width": 170, "height": 120},
    )

    # Add elements...
    fig.save()
    logger.success("Done!")

if __name__ == "__main__":
    main()
```

---

## Coordinate System

```
(0,0) ──────────────────► x_mm
  │
  │   ┌─────────────────────────┐
  │   │  Figure Canvas          │
  │   │  (170mm × 120mm)        │
  │   │                         │
  │   │   Element A (10, 10)    │
  │   │   └── annotation (5, 3) │  <- absolute: (15, 13)
  │   │                         │
  │   └─────────────────────────┘
  ▼
y_mm
```

**Key**: Origin at top-left, positions in millimeters.

---

## Bundle Structure

```
my_figure.zip.d/
├── spec.json           # WHAT to plot (elements, layout)
├── encoding.json       # Data -> visual channel bindings
├── theme.json          # Aesthetics (colors, fonts)
├── data/
│   └── data_info.json  # Data metadata
├── stats/
│   └── stats.json      # Statistical results
├── cache/
│   ├── geometry_px.json    # Hit areas for GUI
│   ├── render_manifest.json
│   └── hitmap.png
├── exports/
│   ├── figure.png
│   ├── figure.svg
│   └── figure.pdf
└── children/           # Embedded plot bundles
    └── plot_A.zip.d/
```

---

## Related Documentation

- [scitex.fig README](../../src/scitex/fig/README.md) - Full API reference
- [scitex.io.bundle README](../../src/scitex/io/bundle/README.md) - Bundle I/O operations
- [Tests](../../tests/scitex/fig/) - Test coverage

<!-- EOF -->
