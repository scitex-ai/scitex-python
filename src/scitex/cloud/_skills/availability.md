---
description: How stx.cloud handles optional scitex-cloud dependency — AVAILABLE flag, graceful degradation, and installation.
---

# Cloud Availability and Optional Dependency

`stx.cloud` delegates all implementation to the separate `scitex-cloud` package (Django web application). The hub package (`scitex`) never hard-requires it.

## AVAILABLE Flag

```python
import scitex as stx

if stx.cloud.AVAILABLE:
    status = stx.cloud.health_check()
else:
    print("scitex-cloud not installed")
```

`stx.cloud.AVAILABLE` is `True` only when `scitex-cloud` is importable. It is set at module import time and never changes after that.

## Behavior When Not Installed

Every public function raises `ImportError` with an actionable message:

```
ImportError: scitex-cloud package not installed.
Install with: pip install scitex-cloud
Original error: No module named 'scitex_cloud'
```

No silent failures. No fallback behavior.

## Installation

```bash
pip install scitex-cloud
```

## Environment Branding

`stx.cloud.__init__` sets two environment variables before attempting to import `scitex-cloud`. These allow the downstream package to display the correct brand name in logs and UI:

| Variable | Default value |
|----------|---------------|
| `SCITEX_CLOUD_BRAND` | `"scitex.cloud"` |
| `SCITEX_CLOUD_ALIAS` | `"cloud"` |

These are set with `os.environ.setdefault`, so they can be overridden by the caller before importing `scitex`.

## Architecture

```
scitex (hub)
  └── stx.cloud  (thin wrapper)
        └── scitex_cloud  (spoke package, Django app)
              └── scitex_cloud.api.CloudClient
```

All logic lives in `scitex_cloud`. The wrapper in `stx.cloud` only:
1. Sets brand env vars
2. Imports and re-exports `get_version`, `health_check`
3. Wraps `CloudClient` methods as module-level functions
4. Provides stub functions that raise `ImportError` when the package is absent
