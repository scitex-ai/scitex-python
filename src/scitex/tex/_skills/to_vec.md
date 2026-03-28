---
description: Convert a string to LaTeX vector notation (\overrightarrow{\mathrm{...}}). Supports automatic fallback to mathtext or unicode when a system LaTeX engine is unavailable.
---

# to_vec / safe_to_vec

Convert a string to LaTeX vector notation with configurable fallback.

## to_vec

```python
to_vec(
    v_str: str,
    enable_fallback: bool = True,
    fallback_strategy: str = "auto",
) -> str
```

**Parameters**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `v_str` | `str` | required | String to format as a vector (e.g. `"AB"`, `"v"`) |
| `enable_fallback` | `bool` | `True` | When `True`, applies fallback rendering if LaTeX is unavailable |
| `fallback_strategy` | `str` | `"auto"` | How to handle rendering failure (see table below) |

**Returns** `str` — LaTeX string, or fallback representation if LaTeX is unavailable.

**Fallback strategies**

| Strategy | Behaviour | Example output |
|----------|-----------|---------------|
| `"auto"` | Try mathtext; if that fails, use unicode | `$\overrightarrow{\mathrm{AB}}$` or `AB⃗` |
| `"mathtext"` | Wrap in `$...$` for matplotlib mathtext | `$\overrightarrow{\mathrm{AB}}$` |
| `"unicode"` | Unicode combining right arrow above (U+20D7) | `AB⃗` |
| `"plain"` | Plain-text wrapper | `vec(AB)` |

When `enable_fallback=False`, the function returns the raw LaTeX string regardless of system capabilities:
`\overrightarrow{\mathrm{AB}}`

**Function is decorated** with `@latex_fallback_decorator(fallback_strategy="auto", preserve_math=True)` from `scitex.str._latex_fallback`. When that module is unavailable the decorator is a no-op.

---

## safe_to_vec

Convenience wrapper with explicit fallback control and `enable_fallback` always `True`.

```python
safe_to_vec(
    v_str: str,
    fallback_strategy: str = "auto",
) -> str
```

Equivalent to `to_vec(v_str, enable_fallback=True, fallback_strategy=fallback_strategy)`.

---

## Aliases

`vector_notation` is a module-level alias for `to_vec` (backward compatibility).

---

## Examples

```python
import scitex as stx

# Default — auto fallback
v = stx.tex.to_vec("AB")
# Returns: "$\overrightarrow{\mathrm{AB}}$"
# or "AB⃗" if mathtext fails

# Force unicode output
v = stx.tex.to_vec("v", fallback_strategy="unicode")
# Returns: "v⃗"

# Force plain text (no symbols)
v = stx.tex.to_vec("F", fallback_strategy="plain")
# Returns: "vec(F)"

# Raw LaTeX (no fallback)
v = stx.tex.to_vec("E", enable_fallback=False)
# Returns: "\overrightarrow{\mathrm{E}}"

# Use as axis label in a figure
fig, ax = stx.plt.subplots()
ax.set_xlabel(stx.tex.to_vec("r"))
ax.set_ylabel(stx.tex.to_vec("F"))

# safe_to_vec convenience wrapper
v = stx.tex.safe_to_vec("AB", fallback_strategy="unicode")
# Returns: "AB⃗"

# Backward compat alias
from scitex.tex._to_vec import vector_notation
v = vector_notation("k")   # same as to_vec("k")
```

**Edge case**: empty string returns `""` without further processing.
