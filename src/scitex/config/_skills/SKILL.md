---
name: stx.config
description: Configuration management for SciTeX — YAML-based config, dict-based priority resolver, centralized path manager, and environment variable registry. Both patterns use the same precedence: direct > config > env > default.
---

# stx.config

Configuration management for the SciTeX ecosystem. Two complementary patterns share the same priority order: **direct > config > env > default**.

## Sub-skills

### Priority-based resolver (dict/programmatic)
- [priority-config.md](priority-config.md) — `PriorityConfig`, `get_scitex_dir`, `load_dotenv`: dict-backed resolver with configurable env prefix, type coercion, and sensitive-value masking

### YAML-based configuration (recommended)
- [scitex-config.md](scitex-config.md) — `ScitexConfig`, `get_config`, `load_yaml`: YAML loader with `${VAR:-default}` substitution, dot-notation access, and cascade resolution

### Path management
- [paths.md](paths.md) — `ScitexPaths`, `get_paths`: single source of truth for all SciTeX directories; `resolve()` pattern for configurable module paths

### Environment variable registry
- [env-registry.md](env-registry.md) — `ENV_REGISTRY`, `EnvVar`, `generate_template`, `get_env_docs`, `get_env_by_module`, `get_all_modules`: typed registry of all `SCITEX_*` variables with documentation and template generation

---

## Quick reference

```python
import scitex as stx
from scitex.config import (
    ScitexConfig, get_config,
    ScitexPaths, get_paths,
    PriorityConfig, get_scitex_dir, load_dotenv,
    ENV_REGISTRY, EnvVar, generate_template, get_env_docs,
    get_env_by_module, get_all_modules,
)

# YAML-based (recommended)
config = get_config()
level  = config.resolve("logging.level", default="INFO")
debug  = config.resolve("debug.enabled", default=False, type=bool)

# Path manager
paths  = get_paths()            # or stx.PATHS
print(paths.logs)               # ~/.scitex/logs
print(paths.scholar_library)    # ~/.scitex/scholar/library
cache  = paths.resolve("cache", user_provided_path)  # direct > default pattern

# Dict-based resolver
cfg    = PriorityConfig({"port": 3000}, env_prefix="MYAPP_")
port   = cfg.resolve("port", default=8000, type=int)

# Environment variable template
print(generate_template(include_sensitive=False))
```
