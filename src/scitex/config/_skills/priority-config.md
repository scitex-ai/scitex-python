---
name: config-priority-config
description: PriorityConfig — dict-based configuration resolver with precedence hierarchy (direct > config_dict > env > default). Also covers load_dotenv and get_scitex_dir helpers.
---

# PriorityConfig

Dict-based configuration resolver. Precedence order: direct > config_dict > env > default.

Defined in `scitex/config/_PriorityConfig.py`.

---

## PriorityConfig

```python
PriorityConfig(
    config_dict: dict | None = None,
    env_prefix: str = "",
    auto_uppercase: bool = True,
)
```

**Parameters**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `config_dict` | `dict` or `None` | `None` | Base configuration values |
| `env_prefix` | `str` | `""` | Prefix prepended to env var names during lookup (e.g., `"SCITEX_"`) |
| `auto_uppercase` | `bool` | `True` | Uppercase the key when constructing the env var name |

### resolve

```python
resolve(
    key: str,
    direct_val: Any = None,
    default: Any = None,
    type: Type = str,
    mask: bool | None = None,
) -> Any
```

Returns the first non-None value in priority order:

1. `direct_val` (if not None)
2. `config_dict[key]` (if present)
3. Environment variable `{env_prefix}{KEY}` (if set)
4. `default`

Type coercion via `type` applies only to values read from environment variables. The resolved key, source, and display value are appended to `resolution_log`.

**Sensitive key auto-masking**: Keys containing `API`, `PASSWORD`, `SECRET`, `TOKEN`, `KEY`, `PASS`, `AUTH`, `CREDENTIAL`, `PRIVATE`, or `CERT` (case-insensitive) are masked in the log. Override with `mask=False`.

**Env key construction**: dots in `key` become underscores: `"axes.width_mm"` → `SCITEX_AXES_WIDTH_MM`.

**Type conversions**

| `type` | Input | Output |
|--------|-------|--------|
| `int` | `"3"` | `3` |
| `float` | `"1.5"` | `1.5` |
| `bool` | `"true"`, `"1"`, `"yes"` | `True` |
| `list` | `"a,b,c"` | `["a", "b", "c"]` |
| `str` | anything | unchanged string |

### Other methods

```python
get(key: str) -> Any                # Direct dict lookup (no env, no default)
print_resolutions() -> None         # Print resolution log to stdout
clear_log() -> None                 # Clear resolution_log list
```

**Example**

```python
from scitex.config import PriorityConfig
import os

config = PriorityConfig(
    config_dict={"port": 3000, "debug": True},
    env_prefix="MYAPP_",
)

# direct_val wins
port = config.resolve("port", direct_val=9000, default=8000, type=int)
# -> 9000

# config_dict wins over env
port = config.resolve("port", default=8000, type=int)
# -> 3000

# env wins over default when config_dict has no entry
os.environ["MYAPP_TIMEOUT"] = "30"
timeout = config.resolve("timeout", default=10, type=int)
# -> 30

# default when nothing else set
retries = config.resolve("retries", default=3, type=int)
# -> 3

config.print_resolutions()
# Configuration Resolution Log:
# --------------------------------------------------
# port                 = 9000                (direct)
# port                 = 3000                (config_dict)
# timeout              = 30                  (env:MYAPP_TIMEOUT)
# retries              = 3                   (default)
```

---

## get_scitex_dir

```python
get_scitex_dir(direct_val: str | None = None) -> Path
```

Resolve the SciTeX base directory. Calls `load_dotenv()` first to pick up `.env` files, then applies priority: direct_val > `SCITEX_DIR` env var > `~/.scitex`.

```python
from scitex.config import get_scitex_dir

base = get_scitex_dir()                    # -> ~/.scitex (default)
base = get_scitex_dir("/data/scitex")      # -> /data/scitex (direct override)
# SCITEX_DIR=/mnt/nas python script.py    # -> /mnt/nas (env override)
```

---

## load_dotenv

```python
load_dotenv(dotenv_path: str | None = None) -> bool
```

Load environment variables from a `.env` file. Already-set shell variables are **not** overridden (env takes precedence over `.env`).

Search order when `dotenv_path` is `None`:
1. `./.env` (current working directory)
2. `~/.env` (home directory)

Returns `True` if a file was found and loaded, `False` otherwise.

Supports:
- `KEY=value`
- `export KEY=value`
- Single and double quoted values
- `#` comment lines and blank lines

```python
from scitex.config import load_dotenv

loaded = load_dotenv()               # auto-search
loaded = load_dotenv("/etc/scitex.env")  # explicit path
```
