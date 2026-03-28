---
description: Create script-relative output paths with mk_spath / get_spath. Keeps outputs co-located with the generating script under a <stem>_out/ directory.
---

# Session-Relative Output Paths

## mk_spath

Generate an output path that is co-located with the calling script. The function inspects the call stack to find the calling script, then places the output under `<script_stem>_out/<sfname>`.

```python
mk_spath(sfname: str | Path, makedirs: bool = False) -> Path
```

**Parameters**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `sfname` | `str` or `Path` | required | Relative filename or sub-path for the output (e.g. `"results.csv"`, `"plots/fig1.png"`) |
| `makedirs` | `bool` | `False` | If `True`, create all parent directories before returning |

**Returns** `Path` — the full output path.

**Directory convention**

Given a calling script at `/home/user/proj/analysis.py`:

```
/home/user/proj/
    analysis.py          <- calling script
    analysis_out/        <- auto-derived output directory
        results.csv
        plots/
            fig1.png
```

**IPython / Jupyter behavior**

When called from IPython or Jupyter, the caller path cannot be determined. In that case `mk_spath` uses `/tmp/fake-<USER>.py` as the stand-in caller, so output ends up at `/tmp/fake-<USER>_out/<sfname>`.

**Examples**

```python
import scitex as stx

# In /home/user/proj/analysis.py:

# Get the output path (directories not yet created)
out = stx.path.mk_spath("results.csv")
# Path('/home/user/proj/analysis_out/results.csv')

# Get path and create parent directories immediately
fig_path = stx.path.mk_spath("plots/fig1.png", makedirs=True)
# Path('/home/user/proj/analysis_out/plots/fig1.png')
# -> '/home/user/proj/analysis_out/plots/' is created

# Use in combination with stx.io.save
import numpy as np
data = np.random.randn(100)
stx.io.save(data, stx.path.mk_spath("data.npy", makedirs=True))
```

---

## get_spath

Alias for `mk_spath` kept for backward compatibility.

```python
get_spath(sfname: str | Path, makedirs: bool = False) -> Path
```

Identical to `mk_spath` in every way. Prefer `mk_spath` in new code.
