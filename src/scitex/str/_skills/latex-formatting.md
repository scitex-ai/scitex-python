---
description: Wrap strings and numbers in LaTeX math mode ($...$) and add hat notation. Pure string formatting — no LaTeX installation required.
---

# LaTeX Formatting

These functions wrap strings in LaTeX math-mode delimiters (`$...$`). They perform pure string formatting and do not render LaTeX; for rendering with fallback see [latex-fallback.md](latex-fallback.md).

---

## to_latex_style

Wrap a string or number in LaTeX math mode.

```python
to_latex_style(str_or_num) -> str
latex_style = to_latex_style  # backward-compat alias
safe_to_latex_style = to_latex_style  # identical; no fallback needed for pure formatting
```

**Parameters**

| Parameter | Type | Description |
|-----------|------|-------------|
| `str_or_num` | `str` or numeric | Value to wrap |

**Behavior**

- Falsy values (except `0`) return `""`.
- Already-wrapped strings (starts and ends with `$`) are returned unchanged (no double-wrapping).
- Numbers are converted with `str()` before wrapping.

**Examples**

```python
import scitex as stx

stx.str.to_latex_style("aaa")      # '$aaa$'
stx.str.to_latex_style("x^2")      # '$x^2$'
stx.str.to_latex_style(123)         # '$123$'
stx.str.to_latex_style("$x$")      # '$x$'   (no double-wrapping)
stx.str.to_latex_style("")          # ''
stx.str.to_latex_style(0)           # '$0$'

# Alias
stx.str.latex_style("alpha")        # '$alpha$'
```

---

## add_hat_in_latex_style

Wrap a string or number in LaTeX hat notation: `$\hat{...}$`.

```python
add_hat_in_latex_style(str_or_num) -> str
hat_latex_style = add_hat_in_latex_style  # backward-compat alias
safe_add_hat_in_latex_style = add_hat_in_latex_style  # identical
```

**Parameters**

| Parameter | Type | Description |
|-----------|------|-------------|
| `str_or_num` | `str` or numeric | Value to wrap with hat |

**Behavior**

- Falsy values (except `0`) return `""`.
- Input is NOT checked for existing `$` wrapping; always produces `$\hat{input}$`.

**Examples**

```python
import scitex as stx

stx.str.add_hat_in_latex_style("aaa")  # '$\\hat{aaa}$'
stx.str.add_hat_in_latex_style("x")    # '$\\hat{x}$'
stx.str.add_hat_in_latex_style(1)      # '$\\hat{1}$'
stx.str.add_hat_in_latex_style("")     # ''

# Alias
stx.str.hat_latex_style("mu")          # '$\\hat{mu}$'
```

---

## Alias Reference

| Exported name | Points to |
|---|---|
| `latex_style` | `to_latex_style` |
| `hat_latex_style` | `add_hat_in_latex_style` |
| `safe_to_latex_style` | `to_latex_style` (identical) |
| `safe_add_hat_in_latex_style` | `add_hat_in_latex_style` (identical) |

The `safe_*` variants exist for API consistency with the fallback system; since these functions are pure string formatters they never fail.
