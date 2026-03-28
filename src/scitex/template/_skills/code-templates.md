---
description: Retrieve ready-to-use Python code snippets for @stx.session scripts, I/O, config, modules, and each major stx module (plt, stats, scholar, etc.).
---

# Code Templates

`CODE_TEMPLATES` is a registry of 14 ready-to-use Python (and YAML) code snippets. Each template has a string `content` with `{timestamp}`, `{filepath}`, `{filename}`, `{filename_stem}`, and `{docstring}` format placeholders that are filled in at retrieval time.

## Listing Available Templates

```python
import scitex as stx

templates = stx.template.list_code_templates()
# Returns list of dicts: id, name, description, filename, usage
for t in templates:
    print(f"{t['id']:20s}  {t['description']}")
```

Output:
```
session               @stx.session decorated script with auto CLI, config injection, and output tracking
io                    Demonstrates stx.io.save() and stx.io.load() for 30+ file formats
config                YAML configuration file for @stx.session scripts
session-minimal       Minimal @stx.session script with essential injections only
session-plot          @stx.session script optimized for figure generation with auto CSV export
session-stats         @stx.session script for statistical testing with publication-ready output
module                Standard Python module with docstring, type hints, and exports
plt                   stx.plt usage for publication-ready figures with automatic CSV export
stats                 stx.stats usage for publication-ready statistical analysis (23 tests)
scholar               stx.scholar usage for literature management
audio                 stx.audio usage
capture               stx.capture usage
diagram               stx.diagram usage
canvas                stx.canvas usage
writer                stx.writer usage
```

## Retrieving a Single Template

```python
def get_code_template(
    template_id: str,
    filepath: Optional[str] = None,
    docstring: Optional[str] = None,
) -> str
```

- `template_id`: one of the IDs listed above
- `filepath`: inserted into the file header comment (defaults to template's own `filename`)
- `docstring`: replaces the default `"Description of this script/module"`
- Raises `ValueError` if `template_id` is unknown

```python
# Minimal session — paste into a new .py file
code = stx.template.get_code_template("session-minimal")

# Full session with custom path and docstring
code = stx.template.get_code_template(
    "session",
    filepath="./scripts/analysis.py",
    docstring="Run primary analysis pipeline.",
)
print(code)
```

## Getting All Templates at Once

```python
all_code = stx.template.get_all_templates()
# Returns one string: header + each template's usage note + fenced code block
# Priority order: session, io, config, session-minimal, session-plot,
#                 session-stats, module, plt, stats, scholar, audio,
#                 capture, diagram, canvas, writer
```

## Template Reference

### session

Full `@stx.session` script. Injects `CONFIG`, `plt`, `COLORS`, `rng`, `logger`.

```python
@stx.session
def main(
    # n_samples=100,               # Optional -> CLI --n-samples
    CONFIG=stx.INJECTED,           # From ./config/*.yaml
    plt=stx.INJECTED,
    COLORS=stx.INJECTED,
    rngg=stx.INJECTED,
    logger=stx.INJECTED,
):
    logger.info(f"Session ID: {CONFIG.ID}")
    logger.info(f"Output dir: {CONFIG.SDIR_OUT}")
    # stx.io.save(fig, "figure.png")  -> script_out/figure.png
    return 0
```

Key injected paths:
- `CONFIG.SDIR_OUT` — output root (pass to `stx.io.save`)
- `CONFIG.SDIR_RUN` — session run dir (logs, config snapshots)
- `CONFIG.ID` — session ID string like `2025Y-01M-20D-10h30m00s_XyZ1`

### session-minimal

Only `CONFIG` and `logger` injected. Use when no plotting or stats needed.

```python
@stx.session
def main(
    CONFIG=stx.INJECTED,
    logger=stx.INJECTED,
):
    logger.info(f"Session: {CONFIG.ID}")
    return 0
```

### session-plot

Adds figure creation with `stx.io.save` auto CSV export.

```python
@stx.session
def main(
    n_points=100,
    CONFIG=stx.INJECTED,
    plt=stx.INJECTED,
    COLORS=stx.INJECTED,
    logger=stx.INJECTED,
):
    fig, ax = plt.subplots()
    ax.plot_line(x, y, color=COLORS.blue, label="sin(x)")
    ax.set_xyt("X (radians)", "Y", "Sine Wave")
    stx.io.save(fig, "figure.png", symlink_to="./data")
    # Creates figure.png AND figure.csv automatically
    return 0
```

### session-stats

Statistical analysis workflow including t-test and CSV export.

```python
@stx.session
def main(
    n_samples=30,
    effect_size=0.5,
    CONFIG=stx.INJECTED,
    plt=stx.INJECTED,
    logger=stx.INJECTED,
):
    result = stx.stats.test_ttest_ind(group1, group2, return_as="dataframe")
    stx.io.save(result, "stats_results.csv")
    return 0
```

### io

Demonstrates all major `stx.io.save` / `stx.io.load` patterns.

```python
# DataFrame
stx.io.save(df, "data.csv")
stx.io.save(df, "data.parquet")

# NumPy
stx.io.save(arr, "array.npy")

# Dict/config
stx.io.save(config, "config.yaml")

# Figure with metadata + symlink
stx.io.save(fig, "figure.png", metadata={"experiment": "demo"}, symlink_to="./data")

# Load (any format)
df_loaded = stx.io.load(f"{CONFIG.SDIR_OUT}/data.csv")
img, meta = stx.io.load(f"{CONFIG.SDIR_OUT}/figure.png")
```

### config

YAML file to place in `./config/`. Auto-loaded by `@stx.session`.

```yaml
# config/config.yaml  ->  accessed as CONFIG.config.<section>.<key>
data:
  input_dir: ./data/raw
  output_dir: ./data/processed
analysis:
  n_samples: 100
  threshold: 0.05
  seed: 42
figure:
  dpi: 300
  format: png
  width_mm: 180
  height_mm: 120
logging:
  level: INFO
  save_log: true
```

### module

Bare Python module with NumPy-style docstrings and `__all__`.

```python
from typing import Optional

def function_name(arg1, kwarg1: Optional[str] = None):
    """
    Parameters
    ----------
    arg1 : type
        ...
    Returns
    -------
    type
        ...
    """
    pass

__all__ = ["function_name"]
```

### plt

Five usage patterns for `stx.plt`: direct API, multi-panel, `@stx.session` injection, statistical plots, heatmaps. Includes reference table of key features (enhanced axis methods, auto CSV, color palettes).

### stats

Six usage patterns: two-group, multi-group, correlation, categorical, `@stx.session`, power analysis. Includes full list of all 23 available tests and helper functions.

### scholar / audio / capture / diagram / canvas / writer

Module-specific usage examples for the respective `stx.*` submodules.

## Direct Registry Access

```python
from scitex.template import CODE_TEMPLATES

# Inspect a template without formatting
info = CODE_TEMPLATES["session"]
# Keys: name, description, filename, usage, content (raw format string)
```

## MCP Interface

```
template_get_code_template    — get one template by ID (or "all")
template_list_code_templates  — list all templates with metadata
```

```python
# MCP call equivalent
result = await get_code_template_handler(
    template_id="session",
    filepath="./scripts/my_analysis.py",
    docstring="Analyze EEG data.",
)
# result["content"] contains the formatted code string
```
