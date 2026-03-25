---
name: config-paths
description: ScitexPaths — centralized path manager for all SciTeX directories. All paths derive from $SCITEX_DIR (default ~/.scitex). Covers get_paths, resolve(), ensure_dir(), ensure_all(), and list_all().
---

# ScitexPaths

Centralized path manager. Every directory used by the SciTeX ecosystem is expressed as a property of `ScitexPaths`. All paths derive from `$SCITEX_DIR` (default: `~/.scitex`).

Defined in `scitex/config/_paths.py`.

---

## ScitexPaths

```python
ScitexPaths(base_dir: str | None = None)
```

**Parameters**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `base_dir` | `str` or `None` | `None` | Explicit base directory. If `None`, resolves via `get_scitex_dir()`: `SCITEX_DIR` env var or `~/.scitex`. |

### Path properties

All properties return `Path` objects. They are computed on access — no directories are created on construction.

**Core**

| Property | Path |
|----------|------|
| `base` | `$SCITEX_DIR` |
| `logs` | `$SCITEX_DIR/logs` |
| `cache` | `$SCITEX_DIR/cache` |
| `function_cache` | `$SCITEX_DIR/cache/functions` |
| `capture` | `$SCITEX_DIR/capture` |
| `screenshots` | `$SCITEX_DIR/screenshots` |
| `rng` | `$SCITEX_DIR/rng` |

**Browser**

| Property | Path |
|----------|------|
| `browser` | `$SCITEX_DIR/browser` |
| `browser_screenshots` | `$SCITEX_DIR/browser/screenshots` |
| `browser_sessions` | `$SCITEX_DIR/browser/sessions` |
| `browser_persistent` | `$SCITEX_DIR/browser/persistent` |
| `test_monitor` | `$SCITEX_DIR/test_monitor` |

**Cache specializations**

| Property | Path |
|----------|------|
| `impact_factor_cache` | `$SCITEX_DIR/impact_factor_cache` |
| `openathens_cache` | `$SCITEX_DIR/openathens_cache` |

**Scholar**

| Property | Path |
|----------|------|
| `scholar` | `$SCITEX_DIR/scholar` |
| `scholar_cache` | `$SCITEX_DIR/scholar/cache` |
| `scholar_library` | `$SCITEX_DIR/scholar/library` |

**Writer**

| Property | Path |
|----------|------|
| `writer` | `$SCITEX_DIR/writer` |

### resolve

```python
resolve(
    path_name: str,
    direct_val: str | Path | None = None,
) -> Path
```

Return `direct_val` (expanded via `Path.expanduser()`) if it is not `None`; otherwise return the default path for `path_name`.

`path_name` must match an existing property (raises `ValueError` otherwise).

This is the **recommended pattern** for modules that accept optional path parameters:

```python
from typing import Optional
from scitex.config import get_paths

class MyModule:
    def __init__(self, cache_dir: Optional[str] = None):
        # If caller passed a path, use it. Otherwise use $SCITEX_DIR/cache.
        self.cache_dir = get_paths().resolve("cache", cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
```

### ensure_dir

```python
ensure_dir(path: Path) -> Path
```

Create `path` (including parents) if it does not exist. Returns `path` unchanged.

```python
paths = ScitexPaths()
log_dir = paths.ensure_dir(paths.logs)
```

### ensure_all

```python
ensure_all() -> None
```

Create every standard directory (all 18 paths listed above) in a single call. Idempotent.

```python
from scitex.config import get_paths
get_paths().ensure_all()   # initialize entire ~/.scitex tree
```

### list_all

```python
list_all() -> dict[str, Path]
```

Return a dict mapping every property name to its `Path` value. Useful for inspection and iteration.

```python
paths = ScitexPaths()
for name, path in paths.list_all().items():
    print(f"{name}: {path}")
```

---

## get_paths

```python
get_paths(base_dir: str | None = None) -> ScitexPaths
```

Module-level convenience function. Returns a cached singleton when called with no arguments; creates a new `ScitexPaths` instance when `base_dir` is given.

```python
from scitex.config import get_paths

paths = get_paths()                         # cached default (~/.scitex)
paths = get_paths("/data/project/.scitex")  # new instance for custom root
```

---

## Global PATHS constant

`scitex` exposes a pre-constructed `ScitexPaths` instance as `scitex.PATHS`:

```python
import scitex

print(scitex.PATHS.logs)             # ~/.scitex/logs
print(scitex.PATHS.scholar_library)  # ~/.scitex/scholar/library
print(scitex.PATHS.cache)            # ~/.scitex/cache
```

---

## Directory structure

```
$SCITEX_DIR/                      # default: ~/.scitex
├── browser/
│   ├── persistent/
│   ├── screenshots/
│   └── sessions/
├── cache/
│   └── functions/
├── capture/
├── impact_factor_cache/
├── logs/
├── openathens_cache/
├── rng/
├── scholar/
│   ├── cache/
│   └── library/
├── screenshots/
├── test_monitor/
└── writer/
```

---

## Thread-safe multi-project usage

Pass an explicit `base_dir` to isolate paths per user or project:

```python
from scitex.config import ScitexPaths

user_a = ScitexPaths(base_dir="/data/user_a/.scitex")
user_b = ScitexPaths(base_dir="/data/user_b/.scitex")

proc_a = DataProcessor(cache_dir=user_a.cache)
proc_b = DataProcessor(cache_dir=user_b.cache)
```
