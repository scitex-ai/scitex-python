# Development Tools in stx.dev

The `stx.dev` module contains utilities for SciTeX package developers: module reloading, code flow analysis, pyproject.toml management, and demo plot generation.

## Module Reloading

Useful during interactive development when you want changes to be picked up without restarting the interpreter:

```python
from scitex.dev._reload import reload, reload_auto, reload_stop

# Reload all scitex submodules once
reload()

# Start background auto-reload every 10 seconds (daemon thread)
reload_auto(interval=10)

# Stop auto-reload
reload_stop()
```

## Code Flow Analysis

`CodeFlowAnalyzer` uses AST parsing to trace function call sequences in a Python file:

```python
from scitex.dev._analyze_code_flow import CodeFlowAnalyzer

analyzer = CodeFlowAnalyzer("my_script.py")
# analyzer.execution_flow — list of call steps
# analyzer.sequence — current sequence counter
```

## pyproject.toml Management

```python
from scitex.dev import _pyproject as pyproject

# Load pyproject.toml
pp = pyproject.load()

# Inspect extras
extras = pyproject.get_extras(pp)

# Audit all dependencies
pyproject.print_report()

# Check consistency between heavy/light deps
pyproject.validate_heavy_sync()

# Find problems
duplicates = pyproject.find_duplicates()
missing = pyproject.find_missing_heavy_deps()
```

## Demo Plotters

The `stx.dev.plt` subpackage contains demo scripts for every supported plot type in matplotlib, seaborn, and scitex. These are reference implementations for developers adding new plot types:

```python
from scitex.dev.plt.demo_plotters import plot_mpl_scatter

# Each demo plotter follows the same pattern:
# - Creates sample data
# - Plots using the relevant function
# - Saves output for visual verification
```

Available namespaces:
- `stx.dev.plt.demo_plotters.plot_mpl_*` — matplotlib demos (scatter, hist, boxplot, etc.)
- `stx.dev.plt.demo_plotters.plot_sns_*` — seaborn demos
- `stx.dev.plt.demo_plotters.plot_stx_*` — scitex-specific demos

## Computer Vision Utilities

```python
from scitex.dev.cv import compose, title_card

# compose — assemble frames into a video
# title_card — create a title card image for a video
```

## Ecosystem Management (delegates to scitex-dev)

The SKILL.md-level overview of ecosystem tools (version management, bulk rename, SSH checks) are provided by the `scitex-dev` package and accessed via `stx.dev`. See the existing SKILL.md overview for those.
