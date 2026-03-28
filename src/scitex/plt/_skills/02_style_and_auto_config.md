---
skill: plt.style_and_auto_config
description: Auto-configuration on import, style presets, rcParams cascade, and figrecipe style management.
---

# stx.plt — style and auto-configuration

## Auto-configuration on import

When `import scitex.plt` runs, `_auto_config.configure()` is called exactly once. It:

1. Registers Arial fonts if they are found on the system (falls back to Helvetica / DejaVu Sans)
2. Loads the `SCITEX` figrecipe style preset
3. Applies SciTeX rcParams (font sizes, line widths, DPI, figure size, spines)
4. Sets the colour cycle from `scitex.plt.color.PARAMS`

No manual configuration is needed. The result is that every figure created with
`plt.subplots()` already uses publication-appropriate defaults.

## Style presets

```python
import scitex.plt as plt

# List available figrecipe style presets
presets = plt.list_presets()

# Load a named preset
plt.load_style("SCITEX")          # SciTeX defaults
plt.load_style("nature")          # journal preset (if installed)

# Unload — revert to matplotlib defaults
plt.unload_style()

# Apply a style dict or preset name to the current rcParams
plt.apply_style("SCITEX")
plt.apply_style({"font.size": 8, "lines.linewidth": 0.5})

# STYLE constant — current active style name
print(plt.STYLE)
```

## scitex.plt.styles submodule

The `styles` submodule provides programmatic style management with a
priority cascade: direct value → environment variable → YAML config → default.

```python
from scitex.plt.styles import (
    load_style,
    save_style,
    set_style,
    get_style,
    resolve_style_value,
    SCITEX_STYLE,
    STYLE,
)

# Load current style as a dict suitable for subplots(**style)
style = load_style()
fig, ax = plt.subplots(**style)

# Export active style to YAML
save_style("my_style.yaml")

# Override the global style
set_style({"axes_width_mm": 60, "trace_thickness_mm": 0.3})

# Read a single style value with priority resolution
dpi = resolve_style_value("output.dpi", None, 300)

# SCITEX_STYLE dict — the built-in defaults
print(SCITEX_STYLE)
```

### DPI utilities

```python
from scitex.plt.styles import (
    DPI_SAVE,       # 300
    DPI_DISPLAY,    # 100 (default screen DPI)
    DPI_PREVIEW,    # 150
    get_default_dpi,
    get_display_dpi,
    get_preview_dpi,
)
```

## Environment variable overrides

The style system reads `SCITEX_PLT_*` environment variables and maps them to
`FIGRECIPE_*` equivalents before figrecipe imports:

| env var | effect |
|---|---|
| `SCITEX_PLT_DEBUG_MODE` | Enable figrecipe debug logging |
| `SCITEX_PLT_DEV_REPRESENTATIVE_PLOTS` | Generate representative plots in dev mode |

Any `SCITEX_PLT_<KEY>` automatically maps to `FIGRECIPE_<KEY>`, so figrecipe
env vars work under either prefix.

## Style YAML location

The built-in SCITEX style is defined in:

```
src/scitex/plt/styles/SCITEX_STYLE.yaml
```

Override it by placing a `SCITEX_STYLE.yaml` in your project config directory
and pointing `load_style()` at it.

## seaborn integration

```python
import scitex.plt as plt

# plt.sns is seaborn, pre-configured to use the scitex style
plt.sns.boxplot(data=df, x="group", y="score")
plt.sns.set_theme(style="whitegrid")
```

`plt.sns` is `None` if seaborn is not installed.

## SVG output

```python
plt.enable_svg()          # Set matplotlib backend to SVG
stx.io.save(fig, "fig.svg")
```
