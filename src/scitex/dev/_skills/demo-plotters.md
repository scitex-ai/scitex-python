---
description: Pre-built demo scripts for every matplotlib, seaborn, and scitex plot type. Located in scitex.dev.plt.demo_plotters. Run a demo script to generate a reference figure.
---

# Demo Plotters

Located at `scitex/dev/plt/demo_plotters/`. Each script is a standalone executable that generates a reference figure for one plot type.

## Naming convention

```
plot_{library}_{plot_type}.py
```

| Library prefix | Examples |
|---------------|---------|
| `plot_mpl_*` | `plot_mpl_scatter.py`, `plot_mpl_hist.py`, `plot_mpl_boxplot.py` |
| `plot_sns_*` | `plot_sns_heatmap.py`, `plot_sns_violin.py`, `plot_sns_kdeplot.py` |
| `plot_stx_*` | `plot_stx_mean_ci.py`, `plot_stx_shaded_line.py`, `plot_stx_raster.py` |

## Running a demo

```bash
python src/scitex/dev/plt/demo_plotters/plot_mpl_scatter.py
# Generates scatter_demo.png in the current directory
```

## Listing available demos

```python
import importlib.resources
from scitex.dev.plt import demo_plotters

import pkgutil
demos = [m.name for m in pkgutil.iter_modules(demo_plotters.__path__)]
print(demos)
```

## Use for regression testing

The demo scripts also serve as visual regression tests. Run all of them to confirm that plot rendering works correctly after a refactor.
