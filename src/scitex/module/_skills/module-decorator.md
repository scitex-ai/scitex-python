---
name: stx.module — @module Decorator
description: Mark functions as SciTeX workspace modules with the @module decorator and collect structured outputs.
---

# stx.module — @module Decorator

> **Deprecated.** `scitex.module` is a backward-compatibility shim. New code should import from `scitex_cloud.module`.

The `@module` decorator transforms a function into a SciTeX workspace module. The workspace runner discovers decorated functions, injects runtime values, collects outputs, and serializes results.

## @module decorator

```python
from scitex.module import module, output, html, INJECTED

@module(
    label="EEG Viewer",        # display name in UI
    icon="fa-brain",           # FontAwesome icon class
    category="visualization",  # one of: writing, visualization, data, analysis,
                               #         reference, utility, other
    description="Plots EEG signals",
    version="1.0.0",
    dependencies=["mne"],
)
def eeg_viewer(
    project=INJECTED,   # injected: Path to project directory
    plt=INJECTED,       # injected: matplotlib.pyplot (Agg backend)
    logger=INJECTED,    # injected: logging.Logger
):
    """Shows EEG data from the project."""
    data_path = project / "data/eeg.npy"
    # ... analysis ...
    fig, ax = plt.subplots()
    ax.plot(eeg_data)
    output(fig, title="EEG Signal")              # register a figure
    output(summary_df, title="Summary Stats")    # register a DataFrame
    output(html("<b>Done</b>"), title="Status")  # register HTML
```

## output and html

Inside a `@module` function, call `output()` to register items for display:

```python
from scitex.module import output, html

output(fig, title="My Figure")          # matplotlib Figure → base64 PNG
output(df, title="Results Table")       # DataFrame → HTML table
output("Analysis complete", title="Log") # str → text
output({"k": 1}, title="Config")        # dict → JSON
output(html("<em>note</em>"), title="")  # _SafeHtml → raw HTML
```

Auto-detected types: `figure`, `table`, `text`, `json`, `html`.

## INJECTED sentinel

Parameters with `default=INJECTED` are filled by the module runner at execution time:

| Parameter name | Value injected |
|----------------|---------------|
| `project` | `Path` to the project directory |
| `plt` | `matplotlib.pyplot` with Agg backend |
| `logger` | `logging.Logger("stx.module.user")` |

## ModuleManifest

The manifest is attached to the wrapper as `wrapper._manifest`:

```python
manifest = eeg_viewer._manifest
print(manifest.name)        # "eeg_viewer"
print(manifest.label)       # "EEG Viewer"
print(manifest.category)    # "visualization"
manifest.to_dict()          # JSON-serializable dict
```

## Running a module file

```bash
python -m scitex.module._runner path/to/module.py \
    --project-path /path/to/project \
    --output-dir /tmp/module_out
```

Writes `result.json` containing `manifest`, `outputs`, `error`.
