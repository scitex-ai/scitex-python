---
name: stx.cloud
description: SciTeX Cloud web service integration — health monitoring, web app context, JavaScript evaluation, browser UI control, and matplotlib inline display. Delegates to the optional scitex-cloud package.
user-invocable: false
---

# stx.cloud

Thin wrapper over the `scitex-cloud` spoke package (Django web application). All implementation lives in `scitex_cloud`; this module sets branding env vars, re-exports the public API, and provides stub functions that raise `ImportError` when the package is absent.

**Install the spoke:** `pip install scitex-cloud`

## Sub-skills

### Setup and Availability
- [availability.md](availability.md) — `AVAILABLE` flag, optional dependency pattern, env branding, installation

### Core API
- [health-and-version.md](health-and-version.md) — `health_check()`, `get_version()`
- [context.md](context.md) — `get_context(page, **kw)`: username, page state, available actions
- [browser-control.md](browser-control.md) — `eval_js(code, timeout, **kw)`, `ui_action(steps, delay_ms, **kw)`

### Integration
- [matplotlib-hook.md](matplotlib-hook.md) — `install_matplotlib_hook()`, `uninstall_matplotlib_hook()`: inline figure display in headless cloud sessions

## Public API Summary

```python
import scitex as stx

stx.cloud.AVAILABLE          # bool — True only when scitex-cloud is installed

stx.cloud.get_version()      # -> str
stx.cloud.health_check()     # -> dict

stx.cloud.get_context(page="", **kw)            # -> dict
stx.cloud.eval_js(code, timeout=10, **kw)       # -> dict
stx.cloud.ui_action(steps, delay_ms=900, **kw)  # -> dict
```

## Quick Start

```python
import scitex as stx

if not stx.cloud.AVAILABLE:
    raise RuntimeError("pip install scitex-cloud")

# Verify connection
status = stx.cloud.health_check()
assert status["status"] == "healthy"

# Get current page context
ctx = stx.cloud.get_context()
print(ctx["username"], ctx["actions"])

# Read from the browser
result = stx.cloud.eval_js("document.title")

# Drive UI
stx.cloud.ui_action([
    {"action": "click", "selector": "#submit-btn"},
])
```
