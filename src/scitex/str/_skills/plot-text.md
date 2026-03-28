---
description: Format strings for scientific plot labels and titles — capitalize, handle units, replace underscores, format scientific notation, and check unit consistency.
---

# Plot Text Formatting

These functions produce publication-ready strings for matplotlib axis labels, titles, and annotations. All three formatting functions are decorated with `@latex_fallback_decorator` and gracefully degrade when LaTeX is unavailable.

---

## format_plot_text

General-purpose scientific text formatter.

```python
format_plot_text(
    text: str,
    capitalize: bool = True,
    unit_style: str = "parentheses",
    latex_math: bool = True,
    scientific_notation: bool = True,
    enable_fallback: bool = True,
    replace_underscores: bool = True,
) -> str
```

**Parameters**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `text` | `str` | required | Raw text to format |
| `capitalize` | `bool` | `True` | Capitalize first alphabetic character |
| `unit_style` | `str` | `"parentheses"` | Unit bracket style: `"parentheses"` `()`, `"brackets"` `[]`, or `"auto"` (detect and standardize) |
| `latex_math` | `bool` | `True` | Extract and preserve `$...$` sections from underscore/capitalization processing |
| `scientific_notation` | `bool` | `True` | Convert `1e-3` patterns to `1×10^{-3}` |
| `enable_fallback` | `bool` | `True` | Apply `safe_latex_render` to preserved LaTeX sections |
| `replace_underscores` | `bool` | `True` | Replace `_` with spaces and title-case each word |

**Processing pipeline**

1. Extract `$...$` LaTeX sections into placeholders (if `latex_math=True`)
2. Replace underscores with spaces, title-case each word (if `replace_underscores=True`)
3. Format units according to `unit_style`
4. Capitalize first character (if `capitalize=True`)
5. Format scientific notation (if `scientific_notation=True`)
6. Restore LaTeX sections with optional fallback rendering

**Examples**

```python
import scitex as stx

stx.str.format_plot_text("time (s)")
# 'Time (s)'

stx.str.format_plot_text("voltage [V]", unit_style="brackets")
# 'Voltage [V]'

stx.str.format_plot_text("frequency in Hz", unit_style="auto")
# 'Frequency (Hz)'

stx.str.format_plot_text("signal_power_db")
# 'Signal Power Db'

stx.str.format_plot_text(r"$\alpha$ decay")   # falls back if LaTeX fails
# 'α decay'
```

---

## format_axis_label

Combine a variable name with an optional unit and apply `format_plot_text`.

```python
format_axis_label(
    label: str,
    unit: Optional[str] = None,
    unit_style: str = "parentheses",
    capitalize: bool = True,
    latex_math: bool = True,
    enable_fallback: bool = True,
    replace_underscores: bool = True,
) -> str

axis_label = format_axis_label  # convenient alias
```

**Parameters**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `label` | `str` | required | Variable name / description |
| `unit` | `str` | `None` | Unit string (appended as `(unit)` or `[unit]`) |
| remaining | — | same as `format_plot_text` | Passed through |

**Unit attachment**

- `unit_style="brackets"` → `"{label} [{unit}]"`
- anything else → `"{label} ({unit})"`

The combined string is then processed by `format_plot_text`.

**Examples**

```python
import scitex as stx

stx.str.format_axis_label("time", "s")
# 'Time (s)'

stx.str.format_axis_label("voltage", "V", unit_style="brackets")
# 'Voltage [V]'

stx.str.format_axis_label("temperature", "°C")
# 'Temperature (°C)'

stx.str.format_axis_label("signal_power", "dB")
# 'Signal Power (dB)'

# Alias
stx.str.axis_label("frequency", "Hz")
# 'Frequency (Hz)'
```

---

## format_title

Format a plot title with optional subtitle.

```python
format_title(
    title: str,
    subtitle: Optional[str] = None,
    capitalize: bool = True,
    latex_math: bool = True,
    enable_fallback: bool = True,
    replace_underscores: bool = True,
) -> str

title = format_title  # convenient alias
```

**Parameters**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `title` | `str` | required | Main title text |
| `subtitle` | `str` | `None` | Optional subtitle (joined with `\\n`) |
| remaining | — | same as `format_plot_text` | Passed through |

**Examples**

```python
import scitex as stx

stx.str.format_title("neural spike analysis")
# 'Neural Spike Analysis'

stx.str.format_title("data analysis", "preliminary results")
# 'Data Analysis\\nPreliminary Results'

stx.str.format_title("signal_processing_results")
# 'Signal Processing Results'

# Alias
stx.str.title("EEG power spectrum")
# 'EEG Power Spectrum'
```

---

## scientific_text

Alias for `format_plot_text` with the same signature.

```python
scientific_text(text: str, **kwargs) -> str
```

```python
stx.str.scientific_text("alpha band power")
# 'Alpha Band Power'
```

---

## check_unit_consistency

Validate that two units are compatible for a given mathematical operation and derive the result unit.

```python
check_unit_consistency(
    x_unit: Optional[str] = None,
    y_unit: Optional[str] = None,
    operation: str = "none",
) -> Tuple[bool, str]
```

**Parameters**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `x_unit` | `str` | `None` | First unit |
| `y_unit` | `str` | `None` | Second unit |
| `operation` | `str` | `"none"` | One of `"add"`, `"subtract"`, `"multiply"`, `"divide"`, `"none"` |

**Returns** `(is_consistent: bool, result_unit: str)`

**Operation rules**

| Operation | Same units | Different units |
|-----------|-----------|----------------|
| `"add"` / `"subtract"` | `(True, x_unit)` | `(False, "Units incompatible for …")` |
| `"multiply"` | `(True, "x·y")` | `(True, "x·y")` (dimensionless handled) |
| `"divide"` | Same units → `(True, "1")` | `(True, "x/y")` |
| `"none"` | `(True, "")` | `(True, "")` |

Unit normalization: `"sec"/"second"/"seconds"` → `"s"`, `"volt"/"volts"` → `"V"`, etc.

**Examples**

```python
import scitex as stx

stx.str.check_unit_consistency("m", "s", "divide")
# (True, 'm/s')

stx.str.check_unit_consistency("m", "m", "add")
# (True, 'm')

stx.str.check_unit_consistency("m", "kg", "add")
# (False, 'Units incompatible for addition')

stx.str.check_unit_consistency("m", "second", "divide")
# (True, 'm/s')   — "second" normalizes to "s"
```
