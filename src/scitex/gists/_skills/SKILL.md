---
name: stx.gists
description: Ready-to-paste VBA macro code for SigmaPlot v12.0 figure automation.
---

# stx.gists — Skills Index

The `stx.gists` module contains short code snippets ("gists") for external tools. Currently it provides two VBA macros for SigmaPlot v12.0 that are printed to stdout and then pasted into the SigmaPlot macro editor.

## Sub-skills

| File | Description |
|------|-------------|
| [sigmaplot-macros.md](sigmaplot-macros.md) | Print VBA macros for SigmaPlot figure formatting and color changes |

## Quick Reference

```python
from scitex.gists import sigmacro_process_figure_s, sigmacro_to_blue

# Print a macro that standardizes axis labels, tick sizes, and removes top/right axes
sigmacro_process_figure_s()

# Print a macro that changes the selected plot object's color to blue
sigmacro_to_blue()
```

## Exports

- `sigmacro_process_figure_s()` — format figure panel (title, labels, ticks, axes)
- `sigmacro_to_blue()` — change selected plot color to blue
- `SigMacro_processFigure_S()` — deprecated alias
- `SigMacro_toBlue()` — deprecated alias
