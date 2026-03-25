---
name: str-latex-fallback
description: Robust LaTeX rendering fallback for matplotlib — detect capability, convert LaTeX to mathtext or Unicode, cache state, and decorate functions to auto-recover from LaTeX errors.
---

# LaTeX Fallback

When `text.usetex=True` is configured but LaTeX compilation fails (missing fonts, Node.js conflicts, absent `dvipng`), this module provides graceful degradation to matplotlib mathtext or plain Unicode, without crashing.

---

## Fallback modes

Three global modes control behavior:

| Mode | Behavior |
|------|----------|
| `"auto"` (default) | Detect LaTeX capability at first use; fall back to mathtext if unavailable |
| `"force_mathtext"` | Skip LaTeX entirely; use `$...$` mathtext rendering always |
| `"force_plain"` | Skip LaTeX entirely; strip math notation to plain Unicode |

```python
import scitex as stx

stx.str.set_fallback_mode("force_mathtext")
stx.str.get_fallback_mode()   # "force_mathtext"
```

---

## check_latex_capability

Check whether LaTeX rendering is available and working. Result is cached via `functools.lru_cache(maxsize=1)`.

```python
check_latex_capability() -> bool
```

Returns `True` only when `plt.rcParams["text.usetex"]` is `True` AND a test render of `$x^2$` succeeds without raising.

```python
stx.str.check_latex_capability()  # False if LaTeX not installed
```

Call `stx.str.reset_latex_cache()` to clear the cached result and force re-detection.

---

## set_fallback_mode / get_fallback_mode

```python
set_fallback_mode(mode: str) -> None   # "auto", "force_mathtext", "force_plain"
get_fallback_mode() -> str
```

Setting the mode also clears the capability cache. Raises `ValueError` for unknown modes.

---

## enable_latex_fallback / disable_latex_fallback

Convenience wrappers:

```python
enable_latex_fallback(mode="auto") -> None   # calls set_fallback_mode(mode)
disable_latex_fallback() -> None             # forces _latex_available = True
```

---

## reset_latex_cache

Clear the LRU cache on `check_latex_capability` and reset the internal `_latex_available` flag.

```python
reset_latex_cache() -> None
```

Use after changing matplotlib rcParams or installing LaTeX mid-session.

---

## get_latex_status

Return a diagnostic dictionary.

```python
get_latex_status() -> dict
```

**Returned keys**

| Key | Type | Description |
|-----|------|-------------|
| `latex_available` | `bool` | Result of `check_latex_capability()` |
| `fallback_mode` | `str` | Current mode |
| `usetex_enabled` | `bool` | `plt.rcParams["text.usetex"]` |
| `mathtext_fontset` | `str` | `plt.rcParams["mathtext.fontset"]` |
| `font_family` | `list` | `plt.rcParams["font.family"]` |
| `cache_info` | `dict` | LRU cache statistics |

```python
import scitex as stx
stx.str.get_latex_status()
# {'latex_available': False, 'fallback_mode': 'auto', 'usetex_enabled': False, ...}
```

---

## latex_to_mathtext

Convert a LaTeX string to matplotlib mathtext equivalent. Does not render — just translates syntax.

```python
latex_to_mathtext(latex_str: str) -> str
```

**Conversions applied**

- Greek letters: `\\alpha` → `\alpha`, `\\beta` → `\beta`, etc. (24+ letters)
- Math symbols: `\\pm` → `\pm`, `\\infty` → `\infty`, `\\sum` → `\sum`, etc.
- Functions: `\\sin`, `\\cos`, `\\log`, `\\exp`, etc.
- Formatting: `\textbf{x}` → `\mathbf{x}`, `\textit{x}` → `\mathit{x}`
- Accents: `\hat{x}` → `\hat{x}`, `\overrightarrow{v}` → `\vec{v}`
- Fractions: `\frac{a}{b}` → `\frac{a}{b}`

Outer `$` delimiters are stripped before processing and re-added at the end.

```python
stx.str.latex_to_mathtext(r"$\alpha^2$")   # '$\\alpha^2$'
stx.str.latex_to_mathtext(r"$\hat{x}$")    # '$\\hat{x}$'
```

---

## latex_to_unicode

Convert LaTeX to plain Unicode text. Useful for environments that cannot render any math notation.

```python
latex_to_unicode(latex_str: str) -> str
```

**Conversions applied**

- Full Greek alphabet (lower and upper) → Unicode characters (α β γ … Ω)
- Math symbols: `\pm` → ±, `\times` → ×, `\infty` → ∞, `\partial` → ∂, etc.
- Superscript digits: `^2` → ², `^{-3}` → ⁻³
- Subscript digits: `_1` → ₁, `_{2}` → ₂
- Remaining `\command{content}` → `content` (stripped command)
- Remaining `{}` braces removed

```python
stx.str.latex_to_unicode(r"$\alpha^2 \pm \beta$")  # 'α² ± β'
stx.str.latex_to_unicode(r"$x_1$")                  # 'x₁'
```

---

## safe_latex_render

Render a LaTeX string with automatic fallback when LaTeX fails.

```python
safe_latex_render(
    text: str,
    fallback_strategy: str = "auto",
    preserve_math: bool = True,
) -> str
```

**Parameters**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `text` | `str` | required | Text possibly containing LaTeX |
| `fallback_strategy` | `str` | `"auto"` | One of `"auto"`, `"mathtext"`, `"unicode"`, `"plain"` |
| `preserve_math` | `bool` | `True` | Prefer mathtext over Unicode when math is present |

**Strategy behavior**

| Strategy | When LaTeX fails |
|----------|-----------------|
| `"auto"` | If text has `$` or `\`, try mathtext; fall back to Unicode on failure |
| `"mathtext"` | Always use `latex_to_mathtext` |
| `"unicode"` | Always use `latex_to_unicode` |
| `"plain"` | Strip all special characters after Unicode conversion |

```python
import scitex as stx

stx.str.safe_latex_render(r"$\alpha^2$")
# Returns r"$\alpha^2$" if LaTeX works, else mathtext or unicode fallback

stx.str.safe_latex_render(r"$\mu \pm \sigma$", fallback_strategy="unicode")
# 'μ ± σ'

stx.str.safe_latex_render(r"$x^2$", fallback_strategy="plain")
# 'x2'  (all special chars stripped)
```

---

## latex_fallback_decorator

Decorator that adds transparent LaTeX fallback to any function. If the wrapped function raises a LaTeX-related error, it re-calls the function after converting string arguments with `safe_latex_render` and temporarily setting `text.usetex=False`.

```python
latex_fallback_decorator(
    fallback_strategy: str = "auto",
    preserve_math: bool = True,
) -> Callable
```

**LaTeX error detection** — triggers fallback when the error message contains any of: `"latex"`, `"tex"`, `"dvi"`, `"tfm"`, `"font"`, `"usetex"`, `"kpathsea"`, `"dvipng"`, `"ghostscript"`.

Non-LaTeX errors are re-raised unchanged.

```python
import scitex as stx

@stx.str.latex_fallback_decorator(fallback_strategy="auto")
def set_my_label(ax, text):
    ax.set_xlabel(text)   # may raise if LaTeX broken

# If LaTeX fails, text is converted to mathtext and re-tried with usetex=False
```

---

## LaTeXFallbackError

Exception class raised internally when all fallback mechanisms fail.

```python
class LaTeXFallbackError(Exception): ...
```

You can catch it explicitly if you need to handle complete rendering failure:

```python
try:
    result = stx.str.safe_latex_render(text)
except stx.str.LaTeXFallbackError:
    result = text   # last-resort: pass raw text
```
