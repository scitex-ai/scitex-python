---
name: stx.tex
description: LaTeX utilities — export writer documents to .tex, compile to PDF, preview LaTeX strings as figures, and convert strings to vector notation. Use when working with LaTeX in the SciTeX ecosystem.
user-invocable: false
---

# stx.tex — LaTeX Utilities

Utility functions for LaTeX authoring workflows. Accessed via `import scitex as stx` then `stx.tex.<function>`.

## Sub-skills

### Document Export
- [export.md](export.md) — `export_tex`: convert a SciTeX writer document dict to a `.tex` file with journal presets (IEEE, Elsevier, Springer, APS, MDPI, ACM), image extraction, and optional BibTeX output

### Compilation
- [compile.md](compile.md) — `compile_tex`, `CompileResult`: invoke pdflatex / xelatex / lualatex / latexmk and get back a structured result with success flag, PDF path, and parsed errors/warnings

### String Preview
- [preview.md](preview.md) — `preview`: render a list of LaTeX strings as a matplotlib figure with automatic fallback to mathtext or unicode when a system LaTeX engine is absent

### Vector Notation
- [to_vec.md](to_vec.md) — `to_vec`, `safe_to_vec`: format a string as `\overrightarrow{\mathrm{...}}` with configurable fallback (auto, mathtext, unicode, plain)

## Quick Reference

```python
import scitex as stx

# Export writer doc to .tex (journal preset)
stx.tex.export_tex(writer_doc, "paper.tex", journal_preset="ieee")

# Compile to PDF
result = stx.tex.compile_tex("paper.tex", compiler="latexmk")
if result.success:
    print(result.pdf_path)
else:
    print(result.errors)

# Preview LaTeX expressions as a figure
fig = stx.tex.preview([r"\alpha + \beta", r"\sum_{i=1}^n i"])
stx.plt.show()

# Vector notation for axis labels
ax.set_xlabel(stx.tex.to_vec("r"))   # -> $\overrightarrow{\mathrm{r}}$
```

## Exports

| Name | Kind | Source |
|------|------|--------|
| `export_tex` | function | `_export.py` |
| `compile_tex` | function | `_export.py` |
| `CompileResult` | dataclass | `_export.py` |
| `preview` | function | `_preview.py` |
| `to_vec` | function | `_to_vec.py` |
