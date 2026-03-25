---
description: SigmaPlot macro helpers — SigMacro_processFigure_S applies standard figure processing, SigMacro_toBlue converts colors to blue in SigmaPlot figures.
---

# SigmaPlot Macros

## SigMacro_processFigure_S / sigmacro_process_figure_s

Apply standard figure processing steps to a SigmaPlot figure.

```python
import scitex as stx

# PascalCase version
stx.gists.SigMacro_processFigure_S(figure)

# snake_case alias
stx.gists.sigmacro_process_figure_s(figure)
```

---

## SigMacro_toBlue / sigmacro_to_blue

Convert colors in a SigmaPlot figure to blue.

```python
import scitex as stx

# PascalCase version
stx.gists.SigMacro_toBlue(figure)

# snake_case alias
stx.gists.sigmacro_to_blue(figure)
```

Both PascalCase and snake_case names are exported for compatibility with different calling conventions.
