---
name: config-scitex-config
description: ScitexConfig — YAML-based configuration manager with ${VAR:-default} environment variable substitution and priority resolution (direct > config > env > default). Covers get_config and load_yaml.
---

# ScitexConfig

YAML-based configuration manager. Loads `default.yaml` (or a custom file), substitutes `${VAR:-default}` expressions at load time, then exposes values via `get()` and `resolve()`.

Defined in `scitex/config/_ScitexConfig.py`.

Priority order: direct > config (YAML) > env > default.

---

## ScitexConfig

```python
ScitexConfig(
    config_path: str | Path | None = None,
    env_prefix: str = "SCITEX_",
)
```

**Parameters**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `config_path` | `str`, `Path`, or `None` | `None` | Path to a custom YAML file. If `None` or path does not exist, uses the bundled `default.yaml`. |
| `env_prefix` | `str` | `"SCITEX_"` | Prefix for environment variable lookups inside `PriorityConfig`. |

On construction:
1. `load_dotenv()` is called (loads `.env` if present)
2. YAML is loaded with `${VAR:-default}` substitution
3. Nested keys are flattened to dot-notation (`logging.level`, `debug.enabled`, etc.)
4. A `PriorityConfig` instance is created with the flat dict

### get

```python
get(key: str, default: Any = None) -> Any
```

Direct lookup in the flattened YAML dict. No env or priority logic. Supports dot-notation keys.

```python
config = ScitexConfig()
config.get("logging.level")      # -> "INFO"  (from YAML)
config.get("debug.enabled")      # -> False
config.get("missing.key", "x")   # -> "x"
```

### resolve

```python
resolve(
    key: str,
    direct_val: Any = None,
    default: Any = None,
    type: Type = str,
) -> Any
```

Resolves with full precedence:

1. `direct_val` (if not None)
2. YAML config value for `key`
3. `SCITEX_{KEY_UPPER}` environment variable (dots become underscores)
4. `default`

```python
config = ScitexConfig()

# From YAML default
level = config.resolve("logging.level", default="WARNING")
# -> "INFO"  (YAML wins over default)

# Direct value overrides everything
level = config.resolve("logging.level", direct_val="DEBUG")
# -> "DEBUG"

# Type conversion on env var values
max_size = config.resolve("logging.max_file_size_mb", default=5, type=int)
# -> 10  (from YAML, already an int — no conversion needed)
```

### get_nested

```python
get_nested(*keys: str, default: Any = None) -> Any
```

Traverse the original nested YAML structure. Useful when a key maps to a dict sub-tree rather than a scalar.

```python
config = ScitexConfig()
config.get_nested("browser", "screenshots_dir")
# -> None  (value from YAML, not yet substituted path)

config.get_nested("ui", "level_backends", "error")
# -> ["audio", "desktop", "email"]
```

### Properties

| Property | Type | Description |
|----------|------|-------------|
| `config_path` | `Path` | Path to the loaded YAML file |
| `raw` | `dict` | Original nested dict from YAML |
| `flat` | `dict` | Flattened dot-notation dict |

### print

```python
print() -> None
```

Delegates to `PriorityConfig.print_resolutions()` — shows how each key was resolved.

---

## get_config

```python
get_config(config_path: str | Path | None = None) -> ScitexConfig
```

Module-level convenience function. Returns a cached singleton when called with no arguments; creates a new instance when `config_path` is given.

```python
from scitex.config import get_config

config = get_config()                         # cached default (default.yaml)
config = get_config("/project/my_config.yaml") # new instance from custom file
```

---

## load_yaml

```python
load_yaml(path: Path) -> dict
```

Load a YAML file with `${VAR:-default}` environment variable substitution. This is a standalone function used by `ScitexConfig.__init__`.

Substitution rules:
- `${VAR}` — replaced by `os.getenv("VAR")` or `null` if unset
- `${VAR:-default}` — replaced by `os.getenv("VAR", "default")`
- Boolean literals `true`/`false` and `null` are preserved as YAML types

Requires `pyyaml` (`pip install pyyaml`).

```python
from scitex.config import load_yaml
from pathlib import Path

data = load_yaml(Path("config/settings.yaml"))
# Returns a plain dict with all ${...} expressions substituted
```

---

## default.yaml structure

The bundled `default.yaml` covers:

```yaml
scitex_dir: ${SCITEX_DIR:-"~/.scitex"}

logging:
  level: ${SCITEX_LOG_LEVEL:-"INFO"}
  format: ${SCITEX_LOG_FORMAT:-"%(asctime)s - %(name)s - %(levelname)s - %(message)s"}
  file_logging: ${SCITEX_FILE_LOGGING:-true}
  max_file_size_mb: ${SCITEX_LOG_MAX_SIZE_MB:-10}
  backup_count: ${SCITEX_LOG_BACKUP_COUNT:-5}

debug:
  enabled: ${SCITEX_DEBUG:-false}
  verbose: ${SCITEX_VERBOSE:-false}
  capture_screenshots: ${SCITEX_CAPTURE_SCREENSHOTS:-true}

browser:
  base_dir: ${SCITEX_BROWSER_DIR:-null}
  screenshots_dir: ${SCITEX_BROWSER_SCREENSHOTS_DIR:-null}
  sessions_dir: ${SCITEX_BROWSER_SESSIONS_DIR:-null}
  persistent_dir: ${SCITEX_BROWSER_PERSISTENT_DIR:-null}

scholar:
  base_dir: ${SCITEX_SCHOLAR_DIR:-null}
  cache_dir: ${SCITEX_SCHOLAR_CACHE_DIR:-null}
  library_dir: ${SCITEX_SCHOLAR_LIBRARY_DIR:-null}

writer:
  base_dir: ${SCITEX_WRITER_DIR:-null}

ui:
  default_backend: ${SCITEX_UI_DEFAULT_BACKEND:-"audio"}
  # ... backend_priority list, level_backends, timeouts
```

Dot-notation after flattening: `logging.level`, `debug.enabled`, `browser.base_dir`, `scholar.library_dir`, etc.
