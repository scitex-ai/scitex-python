---
name: stx.cloud
description: SciTeX Cloud web service integration for project management, UI control, and JavaScript evaluation.
---

# stx.cloud

The `stx.cloud` module provides integration with the SciTeX Cloud web service (Django backend). It enables project management, browser UI interaction, JavaScript evaluation, and health monitoring of the cloud platform.

## Python API

```python
import scitex as stx

# Check availability
if stx.cloud.AVAILABLE:
    # Health check
    status = stx.cloud.health_check()

    # Get current web app context
    ctx = stx.cloud.get_context("dashboard")
    print(ctx["username"], ctx["actions"])

    # Evaluate JavaScript in the user's browser
    result = stx.cloud.eval_js("document.title")

    # Perform UI actions
    stx.cloud.ui_action("click", selector="#submit-btn")

    # Get version info
    version = stx.cloud.get_version()
```

## Key Features

- `AVAILABLE` flag — gracefully handles missing `scitex-cloud` package
- `health_check()` — verify cloud service is running
- `get_context(page)` — get current user, page state, and available actions
- `eval_js(code, timeout)` — evaluate JavaScript in the connected browser
- `ui_action(action, selector)` — programmatic UI interaction
- Delegates all implementation to the standalone `scitex-cloud` package
