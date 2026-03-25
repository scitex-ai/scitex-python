---
name: stx.gen
description: General utilities collection in scitex. A legacy module with backward-compatible re-exports. Contains active implementations for tensor normalization, time profiling, dimension manipulation, numeric helpers, data inspection, caching, XML/MATLAB I/O, and interactive tools. Many functions have moved to purpose-specific modules.
user-invocable: false
---

# stx.gen — General Utilities

`stx.gen` is a legacy utility collection. **For new code, import from the specific modules listed in each sub-skill.** Backward-compatible re-exports remain here with deprecation warnings where applicable.

```python
import scitex as stx

# All stx.gen functions are accessible as:
stx.gen.<function_name>(...)
```

---

## Sub-skills

### Active Implementations

- [tensor-normalization.md](tensor-normalization.md) — `to_z`, `to_nanz`, `to_01`, `to_nan01`, `unbias`, `clip_perc`; optional caching layer (`_norm_cache`). Requires `torch`.

- [timestamper.md](timestamper.md) — `TimeStamper` class: callable profiler that records labeled checkpoints with elapsed time in a pandas DataFrame.

- [dim-handler.md](dim-handler.md) — `DimHandler` class: flatten non-target dimensions into a batch axis, compute, then restore original shape. Supports `torch.Tensor` and `numpy.ndarray`. Requires `torch`.

- [numeric-utils.md](numeric-utils.md) — `to_even`, `to_odd`, `to_rank`, `symlog`, `transpose`, `connect_nums`, `float_linspace`.

- [data-inspection.md](data-inspection.md) — `var_info`, `ArrayLike` type alias, `describe` (summary statistics).

- [environment-detection.md](environment-detection.md) — `is_ipython`, `is_script`, `list_packages`; context re-exports (`is_notebook`, `detect_environment`, etc.).

- [caching-decorators.md](caching-decorators.md) — `cache` (lru_cache alias), `alternate_kwarg` (multi-name kwarg support), `wrap` (functools.wraps pass-through).

- [xml-matlab.md](xml-matlab.md) — `xml2dict`, `XmlDictConfig`, `XmlListConfig`; `mat2dict`, `public_keys`, `save_npa`, `mat2npy`, `dir2npy`.

- [interactive-tools.md](interactive-tools.md) — `less` (pager), `src` (source viewer), `paste` (clipboard exec), `embed` (IPython shell), `symlink`, `title2path`.

### Migration Reference

- [deprecated.md](deprecated.md) — Complete table of what moved where: `start`/`close`/`running2finished` → `stx.session`; `ci` → `scitex_stats`; `check_host` → `stx.os`; `run_shellcommand` → `stx.sh`; `list_api` → `stx.introspect`; context functions → `stx.context`.

---

## Quick reference

| Function / Class | Sub-skill | Requires |
|-----------------|-----------|---------|
| `TimeStamper` | [timestamper.md](timestamper.md) | pandas |
| `DimHandler` | [dim-handler.md](dim-handler.md) | torch |
| `to_z`, `to_01`, `clip_perc`, ... | [tensor-normalization.md](tensor-normalization.md) | torch |
| `to_even`, `to_odd`, `symlog` | [numeric-utils.md](numeric-utils.md) | numpy |
| `to_rank` | [numeric-utils.md](numeric-utils.md) | torch |
| `transpose` | [numeric-utils.md](numeric-utils.md) | numpy |
| `connect_nums`, `float_linspace` | [numeric-utils.md](numeric-utils.md) | numpy |
| `var_info`, `ArrayLike` | [data-inspection.md](data-inspection.md) | torch, xarray |
| `describe` | [data-inspection.md](data-inspection.md) | pandas, numpy |
| `is_ipython`, `is_script` | [environment-detection.md](environment-detection.md) | — |
| `list_packages` | [environment-detection.md](environment-detection.md) | pandas |
| `cache` | [caching-decorators.md](caching-decorators.md) | — |
| `alternate_kwarg` | [caching-decorators.md](caching-decorators.md) | — |
| `wrap` | [caching-decorators.md](caching-decorators.md) | — |
| `xml2dict`, `XmlDictConfig` | [xml-matlab.md](xml-matlab.md) | — |
| `mat2dict`, `dir2npy` | [xml-matlab.md](xml-matlab.md) | h5py, scipy |
| `less`, `src`, `paste` | [interactive-tools.md](interactive-tools.md) | IPython / pyperclip |
| `embed` | [interactive-tools.md](interactive-tools.md) | IPython, pyperclip, torch |
| `symlink` | [interactive-tools.md](interactive-tools.md) | — |
| `title2path` | [interactive-tools.md](interactive-tools.md) | — |
| `start`, `close` | [deprecated.md](deprecated.md) | use `@stx.session` |
| `ci` | [deprecated.md](deprecated.md) | use `scitex_stats.descriptive.ci` |
| `check_host`, `is_host` | [deprecated.md](deprecated.md) | use `stx.os` |
| `run_shellcommand` | [deprecated.md](deprecated.md) | use `stx.sh` |
