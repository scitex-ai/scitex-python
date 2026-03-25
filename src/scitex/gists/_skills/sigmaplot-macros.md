---
description: Print ready-to-paste VBA macro code for SigmaPlot v12.0 figure formatting.
---

# stx.gists — SigmaPlot Macros

`stx.gists` contains two functions that print VBA macro code for SigmaPlot v12.0. The macros are pasted into the SigmaPlot macro editor ("Automating Routine Tasks" section of the official docs) and run on the active graph page.

## sigmacro_process_figure_s

Formats the currently active SigmaPlot figure panel:
- Resizes figure to a fixed width/height
- Sets title font size to 8 pt
- Sets X and Y axis label sizes to 8 pt
- Sets X and Y tick label sizes to 7 pt
- Sets tick length and width
- Removes top and right axes

```python
from scitex.gists import sigmacro_process_figure_s

# Prints the complete VBA macro to stdout
sigmacro_process_figure_s()
```

Copy the printed code, open SigmaPlot, go to Tools > Macros, paste, and run.

## sigmacro_to_blue

Changes the color and style of the selected SigmaPlot plot object to blue:
- Detects object type (Scatter/Line, Bar, Stacked Bar, Box)
- Applies blue color `RGB(0, 128, 192)` appropriate to the type
- Sets line thickness (0.12 mm) and scatter point size (0.8 mm)

```python
from scitex.gists import sigmacro_to_blue

sigmacro_to_blue()  # prints VBA to stdout
```

## Color palette in the macro

The `getColor` function inside the printed macro supports these named colors:

| Name | RGB |
|------|-----|
| Blue | (0, 128, 192) |
| Green | (20, 180, 20) |
| Red | (255, 70, 50) |
| Yellow | (230, 160, 20) |
| Purple | (200, 50, 255) |
| Pink | (255, 150, 200) |
| LightBlue | (20, 200, 200) |
| DarkBlue | (0, 0, 100) |
| Brown | (128, 0, 0) |

## Deprecated aliases

Both functions have PascalCase aliases that emit `DeprecationWarning`:

```python
from scitex.gists import SigMacro_processFigure_S, SigMacro_toBlue
# DeprecationWarning: use sigmacro_process_figure_s() instead
SigMacro_processFigure_S()
SigMacro_toBlue()
```
