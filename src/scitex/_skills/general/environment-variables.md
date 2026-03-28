---
description: Environment variable naming convention — SCITEX_<MODULE_NAME>_* prefix rule to avoid namespace collisions across the SciTeX ecosystem.
---

# Environment Variable Naming

All SciTeX packages MUST use the `SCITEX_<MODULE_NAME>_*` prefix for environment variables to avoid namespace collisions.

| Package | Prefix | Example |
|---------|--------|---------|
| scitex-notification | `SCITEX_NOTIFICATION_` | `SCITEX_NOTIFICATION_DEFAULT_BACKEND` |
| scitex-cloud | `SCITEX_CLOUD_` | `SCITEX_CLOUD_HOST` |
| scitex-audio | `SCITEX_AUDIO_` | `SCITEX_AUDIO_BACKEND` |
| scitex-writer | `SCITEX_WRITER_` | `SCITEX_WRITER_OUTPUT_DIR` |
| scitex-scholar | `SCITEX_SCHOLAR_` | `SCITEX_SCHOLAR_EMAIL_FROM` |

## Rules

- Primary prefix: `SCITEX_<MODULE>_*` — always checked first
- Backward-compatible fallbacks (e.g., `SCITEX_NOTIFY_*`) are acceptable but the primary prefix takes precedence
- Never use bare `SCITEX_*` without a module name — reserved for framework-level config
- Show `$ENV_VAR_NAME` in CLI help defaults, not resolved values
- Configuration is external (env vars, config files) — never hardcode secrets or defaults that should be user-configurable
