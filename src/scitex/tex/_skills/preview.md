---
description: Render a list of LaTeX strings as a matplotlib figure. Each string is shown twice — raw and math-formatted. Automatically falls back to mathtext or unicode when a full LaTeX engine is unavailable.
---

# preview

Render LaTeX strings visually in a matplotlib figure with automatic fallback.

```python
preview(
    tex_str_list: str | list[str],
    enable_fallback: bool = True,
) -> matplotlib.figure.Figure
```

**Parameters**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `tex_str_list` | `str \| list[str]` | required | One or more LaTeX strings to preview. A bare string is wrapped in a one-element list. |
| `enable_fallback` | `bool` | `True` | When `True`, runs strings through `safe_latex_render` before passing to matplotlib, avoiding crashes if a system LaTeX installation is absent. |

**Returns** `matplotlib.figure.Figure`

Each input string gets its own subplot (height 3 inches per string, width 10 inches).

For each subplot, the string is displayed in two positions:
- Top row (y=0.7): raw text, run through `safe_latex_render(..., "unicode", preserve_math=False)` if fallback is enabled.
- Bottom row (y=0.3): math-formatted string wrapped in `$...$` (unless already wrapped), run through `safe_latex_render(..., preserve_math=True)` if fallback is enabled.

If rendering of an individual string fails, the subplot shows the raw string and a red error message instead of raising.

**Fallback behaviour**

`preview` is decorated with `@latex_fallback_decorator(fallback_strategy="auto", preserve_math=True)` from `scitex.str._latex_fallback`. When that module is unavailable (ImportError), the decorator is a no-op and strings are passed directly to matplotlib.

**Examples**

```python
import scitex as stx

# Preview a single expression
fig = stx.tex.preview(r"\alpha + \beta = \gamma")
stx.plt.show()

# Preview multiple expressions
expressions = [
    r"x^2 + y^2 = r^2",
    r"\sum_{i=1}^{n} i = \frac{n(n+1)}{2}",
    r"\int_0^\infty e^{-x^2}\,dx = \frac{\sqrt{\pi}}{2}",
    r"\nabla \cdot \mathbf{E} = \frac{\rho}{\varepsilon_0}",
]
fig = stx.tex.preview(expressions)
stx.io.save(fig, "latex_preview.png")

# Disable fallback (will crash if LaTeX not installed)
fig = stx.tex.preview([r"\frac{1}{2}"], enable_fallback=False)

# Check figure layout
fig = stx.tex.preview(["a", "b", "c"])
print(fig.get_size_inches())  # (10, 9)  — 3 strings × 3 inches each
```

**Notes**

- The function uses `scitex.plt.subplots` (not bare `matplotlib.pyplot.subplots`).
- Axes spines are hidden via `ax.hide_spines()`.
- `fig.tight_layout()` is called before returning.
- This function previews LaTeX *string notation* (for figures, axis labels, etc.) not full `.tex` documents. For full document preview use `compile_tex` + a system PDF viewer.
