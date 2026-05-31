#!/usr/bin/env python3
# Timestamp: 2026-05-31
# File: src/scitex/_mcp/_resources_text.py
"""Static markdown bodies for umbrella MCP documentation resources.

Pure data module — no FastMCP coupling. The registration wiring lives in
``scitex._mcp._resources``; the entrypoint only imports that.
"""

from __future__ import annotations

CHEATSHEET = """\
# SciTeX Cheatsheet for AI Agents
=================================

## Import Pattern (ALWAYS use this)
```python
import scitex as stx
import numpy as np
```

## 1. @stx.session - Reproducible Experiment Tracking

The MOST IMPORTANT pattern. Wrap your main function with @stx.session:

```python
@stx.session
def main(
    # User parameters (become CLI arguments automatically)
    input_file="data.csv",       # --input-file (default: data.csv)
    n_samples=100,               # --n-samples (default: 100)

    # INJECTED parameters (auto-provided by session)
    CONFIG=stx.INJECTED,         # Session config with ID, paths
    plt=stx.INJECTED,            # Pre-configured matplotlib
    COLORS=stx.INJECTED,         # Color palette
    rngg=stx.INJECTED,            # Seeded random generator
    logger=stx.INJECTED,         # Session logger
):
    \"\"\"This docstring becomes --help description.\"\"\"

    data = stx.io.load(input_file)
    results = process(data, n_samples)

    stx.io.save(results, "results.csv")
    stx.io.save(fig, "plot.png", symlink_to="./data")

    return 0  # Exit status

if __name__ == "__main__":
    main()  # CLI mode when no args passed
```

## 2. stx.io - Universal File I/O (30+ formats)

```python
stx.io.save(df, "data.csv")           # DataFrame -> CSV
stx.io.save(arr, "data.npy")          # NumPy array
stx.io.save(obj, "data.pkl")          # Any Python object
stx.io.save(fig, "plot.png")          # Figure + auto CSV
data = stx.io.load("data.csv")
```

## 3. stx.plt - Publication-Ready Figures (Auto CSV Export)

```python
fig, ax = stx.plt.subplots()
ax.stx_line(x, y, label="Signal")     # Tracked: exports to CSV
ax.set_xyt("X axis", "Y axis", "Title")
stx.io.save(fig, "plot.png")          # Saves plot.png + plot.csv
fig.close()
```

## 4. stx.stats - Publication Statistics (23 tests)

```python
result = stx.stats.test_ttest_ind(group1, group2, return_as="dataframe")
result = stx.stats.test_anova(*groups, return_as="latex")
```

## 5. stx.scholar - Literature Management

```bash
scitex scholar bibtex papers.bib --project myresearch --num-workers 8
```

## Quick Tips

1. ALWAYS use `import scitex as stx`
2. ALWAYS wrap main functions with `@stx.session`
3. ALWAYS use `stx.io.save()` and `stx.io.load()` for files
4. ALWAYS use `stx.plt.subplots()` for figures
5. ALWAYS use `ax.stx_*` methods for auto CSV export
6. ALWAYS return exit status (0 for success) from main
"""

SESSION_TREE = """\
# @stx.session Output Directory Structure
==========================================

```
script.py                          # Your script
script_out/                        # Output directory (auto-created)
├── output.npy                     # Your saved files (ROOT level)
├── figure.png                     # Figures
├── figure.csv                     # Auto-exported plot data
├── RUNNING/                       # Currently running sessions
├── FINISHED_SUCCESS/              # Completed sessions
│   └── <session_id>-main/
│       ├── CONFIGS/
│       │   ├── CONFIG.pkl
│       │   └── CONFIG.yaml
│       └── logs/
│           ├── stdout.log
│           └── stderr.log
└── FINISHED_FAILED/               # Failed sessions
data/                              # Central navigation via symlinks
└── output.npy -> ../script_out/output.npy
```

## Key Points

1. Session ID: `YYYY'Y'-MM'M'-DD'D'-HH'h'MM'm'SS's'_XXXX-funcname`
2. Files saved with `stx.io.save(obj, "filename")` go to `script_out/` ROOT
3. `symlink_to="./data"` accumulates outputs from multiple scripts
4. CONFIG (`CONFIG=stx.INJECTED`): ID, FILE, SDIR_OUT, PID, ARGS
5. YAML files in `./config/*.yaml` auto-load into CONFIG (dot access)
6. On success RUNNING -> FINISHED_SUCCESS; on error -> FINISHED_FAILED
"""

MODULE_IO = """\
# stx.io - Universal File I/O
==============================

```python
stx.io.save(obj, path, **kwargs)  # Save any object
stx.io.load(path, **kwargs)       # Load any file
```

- Extension determines handler: `stx.io.save(df, "data.csv")` -> CSV
- `verbose=True` logs `SUCC: Saved to: ...`
- PNG/JPEG support embedded `metadata={...}`
- `symlink_to="./data"` creates symlinks
- Saving a figure also exports plotted data as `.csv`

## Common Formats
- `.csv`, `.xlsx`, `.parquet` - DataFrames
- `.npy`, `.npz`, `.h5` - Arrays
- `.pkl`, `.json`, `.yaml` - Objects
- `.png`, `.jpg`, `.pdf`, `.svg` - Figures
"""

MODULE_PLT = """\
# stx.plt - Publication-Ready Figures
======================================

```python
fig, ax = stx.plt.subplots()
ax.stx_line(x, y, label="Signal")
ax.set_xyt("X axis", "Y axis", "Title")
stx.io.save(fig, "plot.png")  # creates plot.png + plot.csv
fig.close()
```

## Tracked Methods (stx_ prefix; auto CSV export)
stx_line, stx_scatter, stx_bar, stx_errorbar, stx_hist,
stx_boxplot, stx_violinplot, stx_imshow
"""

MODULE_STATS = """\
# stx.stats - Publication Statistics
=====================================

23 tests with assumption checking, effect sizes, CIs, output formats.

```python
result = stx.stats.test_ttest_ind(g1, g2)
result = stx.stats.test_mannwhitneyu(g1, g2)   # Non-parametric
result = stx.stats.test_anova(g1, g2, g3)
result = stx.stats.test_pearsonr(x, y)
result = stx.stats.test_ttest_ind(g1, g2, return_as="latex")
```

Result: statistic, p_value, effect_size, ci_low/ci_high, power.
"""

MODULE_SCHOLAR = """\
# stx.scholar - Literature Management
======================================

```bash
scitex scholar bibtex papers.bib --project myresearch --num-workers 8
```

Enriches BibTeX with abstracts, DOIs, journals, impact factors; downloads PDFs.

## MCP Tools
scholar_search_papers, scholar_enrich_bibtex, scholar_download_pdf,
scholar_fetch_papers, scholar_parse_pdf_content
"""

MODULE_SESSION = """\
# stx.session - Reproducible Experiment Tracking
=================================================

```python
@stx.session
def main(input_file="data.csv", CONFIG=stx.INJECTED, plt=stx.INJECTED):
    \"\"\"Docstring becomes --help.\"\"\"
    stx.io.save(results, "output.csv", symlink_to="./data")
    return 0
```

CONFIG: ID, FILE, SDIR_OUT, PID, ARGS.
YAML in `./config/*.yaml` auto-loads into CONFIG (dot access).
Always return exit status (0 for success).
"""

MODULE_DOCS = {
    "io": MODULE_IO,
    "plt": MODULE_PLT,
    "stats": MODULE_STATS,
    "scholar": MODULE_SCHOLAR,
    "session": MODULE_SESSION,
}

IO_FORMATS = """\
# stx.io Supported Formats
===========================

## Data
.csv .tsv .xlsx .json .yaml/.yml .pkl/.pickle .npy .npz .h5/.hdf5
.zarr .parquet .feather

## Images
.png .jpg/.jpeg .tiff/.tif .pdf .svg

## Scientific (load)
.edf (EEG) .fif (MNE) .set (EEGLAB) .mat (MATLAB)

## PyTorch
.pt .pth

Notes:
- Extension determines handler.
- PNG/JPEG support embedded metadata.
- Saving figures also exports plotted data as CSV.
- `symlink_to="./data"` creates symlinks.
"""

FIGRECIPE_INTEGRATION = """\
# stx.plt - Powered by FigRecipe
=================================

stx.plt records matplotlib calls to YAML recipes for reproducibility.

## MCP Declarative Spec (via plt_plot tool) — prefer CSV column input
```yaml
plots:
  - type: scatter
    data_file: results.csv
    x: time
    y: measurement
    color: blue
```
Workflow: Python writes CSV -> MCP reads columns -> creates figure.

## For Detailed FigRecipe Docs
- figrecipe://cheatsheet
- figrecipe://api/core
- figrecipe://mcp-spec

## Supported Plot Types
line, scatter, bar, barh, hist, boxplot, violinplot, imshow, heatmap,
errorbar, fill_between, contour, contourf, pie, stem
"""

# EOF
