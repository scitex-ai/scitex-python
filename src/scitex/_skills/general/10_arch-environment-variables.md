---
name: arch-environment-variables
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

## Feature Flags

All SciTeX feature flags follow the **opt-out** pattern (default enabled, explicitly disable):

| Pattern | Example | Meaning |
|---------|---------|---------|
| `SCITEX_<MODULE>_DISABLE=true` | `SCITEX_OROCHI_DISABLE=true` | Disable a module entirely |
| `SCITEX_MCP_USE_<MODULE>=0` | `SCITEX_MCP_USE_PLT=0` | Disable MCP tool group |

**Convention:**
- Features are **enabled by default** (opt-out)
- Set `DISABLE=true` or `USE_*=0` to turn off
- Never require users to opt-in for core functionality
- Enforce with code (guards, exit), not documentation

### Exceptions (opt-in)

Some features require explicit opt-in due to external dependencies or resource costs:

| Variable | Reason |
|----------|--------|
| `SCITEX_OROCHI_TELEGRAM_BRIDGE_ENABLED` | Telegram bridge connects to external Bot API; must be intentional |
| `SCITEX_SCHOLAR_OPENATHENS_ENABLED` | External authentication service; security-sensitive |
| `SCITEX_NOTIFICATION_TELEGRAM_POLLING_ENABLED` | Long-polling is resource-intensive; opt-in to avoid waste |

These use `_ENABLED=true` to activate. The rule: if a feature touches external services, auth, or consumes resources when idle, it may use opt-in instead.

## Mandatory per-package `NN_env-vars.md` leaf

Every SciTeX package that reads one or more `SCITEX_*` env vars at import or
runtime **MUST** ship an `NN_env-vars.md` leaf inside its
`src/<pkg_snake>/_skills/<pkg>/` directory (next free `NN_`). The leaf lists
every env var the package's source actually reads, as a table:

| Variable | Purpose | Default | Type |
|---|---|---|---|
| `SCITEX_<PKG>_FOO` | One-line purpose | `default` or `—` (required) | string / int / bool / path |

For boolean flags, add a **Feature flags** subsection distinguishing opt-out
(`DISABLE=true` / `USE_*=0`, default enabled) from opt-in (`_ENABLED=true`,
default disabled; justify why).

**Rule:** `NN_env-vars.md` is mandatory for any package that reads one or more
`SCITEX_*` env vars. Link it from the package's `SKILL.md` sub-skill list.

**One-line audit** (run per package, exclude tests / archive):

```bash
grep -rhoE 'SCITEX_[A-Z0-9_]+' scitex-<pkg>/src/ | sort -u
```

Cross-check against the leaf; any var present in source but missing from the
table is a release blocker (see `99_scitex-quality-checklist.md` §15).
