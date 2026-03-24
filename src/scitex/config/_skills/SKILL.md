---
name: stx.config
description: YAML-based and dict-based configuration management with priority ordering and path management.
---

# stx.config

The `stx.config` module provides two complementary configuration patterns: `ScitexConfig` (YAML-based, recommended) and `PriorityConfig` (dict-based). Both use the same priority order: direct arguments > config file > environment variables > defaults.

## Python API

```python
import scitex as stx

# YAML-based configuration (recommended)
config = stx.config.get_config()
log_level = config.resolve("logging.level", default="INFO")
db_url = config.resolve("database.url", default="sqlite:///db.sqlite3")

# Load YAML directly
config = stx.config.ScitexConfig.from_file("config/settings.yaml")

# Centralized path manager
paths = stx.config.get_paths()
print(paths.logs)     # ~/.scitex/logs
print(paths.cache)    # ~/.scitex/cache
cache_dir = paths.resolve("cache", user_provided_override)

# Dict-based configuration
cfg = stx.config.PriorityConfig(
    {"debug": False},
    env_prefix="MYAPP"
)

# Environment variable registry
docs = stx.config.get_env_docs(module="logging")
template = stx.config.generate_template()
```

## Key Features

- `ScitexConfig` — YAML-based config with `${VAR:-default}` env var substitution
- `PriorityConfig` — dict-based config with configurable env prefix
- `ScitexPaths` / `get_paths()` — centralized path manager for logs, cache, data
- `ENV_REGISTRY` — registry of all SciTeX environment variables with documentation
- Priority order: direct > config > env > default (consistent across both patterns)
