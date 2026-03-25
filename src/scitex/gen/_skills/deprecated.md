---
description: Deprecated functions and re-exports in stx.gen — start/close/running2finished (now in stx.session), host utilities (now in stx.os), shell commands (now in stx.sh), and other relocated functions. All trigger DeprecationWarning.
---

# Deprecated Functions and Re-exports

`stx.gen` is a legacy module. Most of its functions have been relocated to purpose-specific modules. This page documents what moved where and the migration path.

---

## Session lifecycle (DEPRECATED)

These forward to `scitex.session` and emit `DeprecationWarning` via `@deprecated`.

| Old name | Replacement | Notes |
|----------|-------------|-------|
| `stx.gen.start(...)` | `stx.session.start(...)` | Old session initializer |
| `stx.gen.close(...)` | `stx.session.close(...)` | Old session finalizer |
| `stx.gen.running2finished(...)` | `stx.session.running2finished(...)` | Moves session output dirs |

```python
# Old code (still works, raises DeprecationWarning)
CONFIG, sys.stdout, sys.stderr, plt, CC = stx.gen.start(sys, plt)
stx.gen.close(CONFIG)

# Recommended
@stx.session
def main(CONFIG=stx.INJECTED, plt=stx.INJECTED, logger=stx.INJECTED):
    ...
```

---

## Host utilities (moved to stx.os)

Re-exported from `scitex.os` — **no deprecation warning currently**, but prefer `stx.os.*` in new code.

| Name | Preferred location |
|------|--------------------|
| `stx.gen.check_host(name)` | `stx.os.check_host` |
| `stx.gen.is_host(name)` | `stx.os.is_host` |
| `stx.gen.verify_host(name)` | `stx.os.verify_host` |

---

## Shell commands (moved to stx.sh)

Re-exported from `scitex.sh` — no deprecation warning, but prefer `stx.sh.*`.

| Name | Preferred location |
|------|--------------------|
| `stx.gen.run_shellcommand(cmd)` | `stx.sh.run_shellcommand` |
| `stx.gen.run_shellscript(path)` | `stx.sh.run_shellscript` |

---

## Statistics (moved to scitex_stats)

| Name | Preferred location |
|------|--------------------|
| `stx.gen.ci(data, alpha=0.05)` | `scitex_stats.descriptive.ci` |

```python
# Old
ci = stx.gen.ci(data, alpha=0.05)

# Preferred
from scitex_stats.descriptive import ci
ci = ci(data, alpha=0.05)
```

---

## Introspection (moved to stx.introspect)

| Name | Preferred location |
|------|--------------------|
| `stx.gen.list_api(pkg)` | `stx.introspect.list_api` |

---

## Environment / context (moved to stx.context)

Re-exported from `scitex.context` for backward compatibility.

| Name | Preferred location |
|------|--------------------|
| `stx.gen.detect_environment()` | `stx.context.detect_environment` |
| `stx.gen.is_notebook()` | `stx.context.is_notebook` |
| `stx.gen.get_notebook_path()` | `stx.context.get_notebook_path` |
| `stx.gen.get_notebook_name()` | `stx.context.get_notebook_name` |
| `stx.gen.get_notebook_directory()` | `stx.context.get_notebook_directory` |
| `stx.gen.get_output_directory()` | `stx.context.get_output_directory` |

See also [environment-detection.md](environment-detection.md) for `is_ipython` and `is_script`, which remain native to `stx.gen`.

---

## String utilities (moved to stx.str)

| Name | Preferred location |
|------|--------------------|
| `stx.gen.title_case(s)` | `stx.str.title_case` |

---

## Path utilities (moved to stx.path)

| Name | Preferred location |
|------|--------------------|
| `stx.gen.symlink(tgt, src)` | Lives in `stx.gen._symlink` (not yet moved); also documented in [interactive-tools.md](interactive-tools.md) |

---

## Optional (require torch)

These are set to `None` at import time if `torch` is not installed. No deprecation warning.

| Name | Notes |
|------|-------|
| `stx.gen.DimHandler` | See [dim-handler.md](dim-handler.md) |
| `stx.gen.embed` | IPython embed with clipboard |
| `stx.gen.to_z`, `to_nanz`, `to_01`, `to_nan01`, `unbias`, `clip_perc` | See [tensor-normalization.md](tensor-normalization.md) |
| `stx.gen.to_rank` | See [numeric-utils.md](numeric-utils.md) |
| `stx.gen.ArrayLike`, `var_info` | See [data-inspection.md](data-inspection.md) |

---

## Summary: where things moved

```
stx.gen.start / close    → @stx.session decorator
stx.gen.ci               → scitex_stats.descriptive.ci
stx.gen.check_host       → stx.os
stx.gen.run_shellcommand → stx.sh
stx.gen.list_api         → stx.introspect
stx.gen.detect_environment / is_notebook / ... → stx.context
stx.gen.title_case       → stx.str
```
