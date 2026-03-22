---
name: scitex
description: Comprehensive Python framework for scientific research automation — session tracking, I/O, plotting, statistics, scholar, and 50+ modules. Use as the unified entry point for scientific workflows.
allowed-tools: mcp__scitex__*
---

# SciTeX: Python Framework for Scientific Research

## Quick Start

```python
import scitex as stx

@stx.session
def main(
    param1="default",      # Auto-CLI: --param1
    CONFIG=stx.INJECTED,   # Auto-injected config from ./config/*.yaml
    plt=stx.INJECTED,      # Pre-configured matplotlib
    logger=stx.INJECTED,   # Session logger
):
    """Docstring becomes --help description."""
    # Outputs auto-organized: script_out/FINISHED_SUCCESS/<session_id>/
    stx.io.save(results, "results.csv")
    return 0
```

## Core Modules

### stx.io — Universal File I/O (30+ formats)

```python
stx.io.save(df, "data.csv")           # DataFrames
stx.io.save(arr, "data.npy")          # NumPy arrays
stx.io.save(fig, "plot.png")          # Figures (+ auto CSV export)
stx.io.save(obj, "data.pkl")          # Any Python object
data = stx.io.load("data.csv")        # Unified loading
CONFIG = stx.io.load_configs("./config/")  # Merge YAML/JSON configs
```

### stx.plt — Publication-Ready Figures

```python
fig, ax = stx.plt.subplots()
ax.plot_line(x, y)                    # Data tracked automatically
ax.set_xyt("X Label", "Y Label", "Title")
stx.io.save(fig, "plot.png")          # Saves plot.png + plot.csv
```

### stx.stats — Publication Statistics (23 tests)

```python
result = stx.stats.test_ttest_ind(g1, g2, return_as="dataframe")
# Returns: p-value, effect size (Cohen's d), CI, normality check, power
result = stx.stats.test_anova(*groups, return_as="latex")
stars = stx.stats.p_to_stars(0.003)   # → "**"
```

### @stx.session — Reproducible Experiment Tracking

```python
@stx.session
def experiment(lr=0.001, epochs=100, CONFIG=stx.INJECTED, plt=stx.INJECTED):
    # Auto: CLI args, logging, output dirs, git hash tracking
    # Run: python experiment.py --lr 0.01 --epochs 200
    pass
```

### stx.scholar — Literature Management

```python
# CLI: scitex scholar bibtex papers.bib --project myresearch
# Enriches BibTeX with abstracts, DOIs, impact factors
# Downloads PDFs, builds citation graphs
```

## Common Workflows

### "Run a reproducible experiment"

```python
import scitex as stx

@stx.session
def train(lr=0.001, batch_size=32, CONFIG=stx.INJECTED, plt=stx.INJECTED, logger=stx.INJECTED):
    logger.info(f"Training with lr={lr}")
    # ... training code ...
    fig, ax = plt.subplots()
    ax.plot_line(epochs, losses)
    ax.set_xyt("Epoch", "Loss", "Training Loss")
    stx.io.save(fig, "loss_curve.png")
    stx.io.save(results_df, "metrics.csv")
    return 0
```

### "Statistical comparison of groups"

```python
import scitex as stx

# Recommend appropriate test
rec = stx.stats.recommend_tests(group1, group2)

# Run test with full reporting
result = stx.stats.test_ttest_ind(group1, group2, return_as="dataframe")
formatted = stx.stats.format_results(result)
```

### "Save and load anything"

```python
import scitex as stx

# Save in any format — auto-detected from extension
stx.io.save(df, "results.csv")
stx.io.save(df, "results.parquet")
stx.io.save(arr, "weights.npy")
stx.io.save(config, "params.yaml")
stx.io.save(fig, "figure.png")  # + figure.csv

# Load back
data = stx.io.load("results.csv")
```

## CLI Commands

```bash
# Main entry point
scitex --help

# Module-specific
scitex io info data.csv
scitex stats recommend group1.csv group2.csv
scitex scholar search "neural oscillations"
scitex template clone research-project ./my-project
scitex browser save-as-pdf https://example.com ./output.pdf

# MCP server (all modules unified)
scitex-mcp-server
```

## Module Index

| Module | Purpose |
|--------|---------|
| `stx.io` | Universal file I/O (30+ formats) |
| `stx.plt` | Publication-ready figures |
| `stx.stats` | Statistical tests (23 tests) |
| `stx.session` | Reproducible experiment tracking |
| `stx.scholar` | Literature management |
| `stx.ai` | LLM APIs and ML tools |
| `stx.dsp` | Digital signal processing |
| `stx.nn` | Neural networks (PyTorch) |
| `stx.cv` | Computer vision |
| `stx.gen` | General utilities |
| `stx.pd` | Pandas extensions |
| `stx.linalg` | Linear algebra |
| `stx.parallel` | Parallel processing |
| `stx.diagram` | Diagram generation |
| `stx.writer` | Academic paper writing (LaTeX) |
| `stx.clew` | Reproducibility verification |
| `stx.cloud` | Cloud service integration |
| `stx.template` | Project templates |
| `stx.capture` | Screenshot capture |
| `stx.browser` | Web automation & page-to-PDF |
| `stx.audio` | Text-to-speech |
| `stx.ui` | User interface utilities |

## Installation

```bash
pip install scitex                    # Core only
pip install scitex[plt]               # + plotting
pip install scitex[stats]             # + statistics
pip install scitex[scholar]           # + literature management
pip install scitex[audio,plt,stats]   # Multiple modules
pip install scitex[all]               # Everything
```
