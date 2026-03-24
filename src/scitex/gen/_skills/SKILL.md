---
name: stx.gen
description: General utilities collection (largely deprecated); prefer specific modules like stx.stats, stx.os, stx.sh.
---

# stx.gen

The `stx.gen` module is a legacy general utilities collection. Many functions have been relocated to more appropriate modules. For new code, use the specific modules directly. Backward-compatible re-exports are provided here with deprecation warnings.

## Python API

```python
import scitex as stx

# Confidence interval (prefer stx.stats.descriptive.ci)
ci = stx.gen.ci(data, alpha=0.05)

# Host checking (prefer stx.os)
stx.gen.check_host("myserver")
stx.gen.is_host("myserver")

# Shell commands (prefer stx.sh)
result = stx.gen.run_shellcommand("ls -la")

# Caching
@stx.gen.cache(max_size=100)
def expensive_fn(x):
    return compute(x)

# IPython detection (prefer stx.context)
stx.gen.is_ipython()
stx.gen.is_script()

# Less pager
stx.gen.less(long_text)

# DimHandler (optional, requires torch)
handler = stx.gen.DimHandler(data, dim_names=["batch", "time", "freq"])
```

## Key Features

- `ci(data, alpha)` — confidence interval (re-exported from `scitex_stats.descriptive`)
- `check_host` / `is_host` / `verify_host` — SSH host utilities (use `stx.os` instead)
- `cache` — simple function caching decorator
- `alternate_kwarg` — accept multiple keyword argument names for the same parameter
- `is_ipython` / `is_script` — environment detection (use `stx.context` instead)
- `DimHandler` — dimension-aware tensor wrapper (optional, requires PyTorch)
- Most functions have moved; this module exists for backward compatibility
