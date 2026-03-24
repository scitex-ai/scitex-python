---
name: stx.browser
description: Playwright-based browser automation helpers for testing, debugging, and visual feedback.
---

# stx.browser

The `stx.browser` module provides Playwright-based browser automation utilities organized into debugging, monitoring, and visual feedback categories. All features require Playwright to be installed.

## Python API

```python
import scitex as stx

# Sync browser session (zombie prevention)
with stx.browser.sync_browser_session() as browser:
    page = browser.new_page()

# Visual feedback during tests
await stx.browser.show_cursor_at_async(page, x=100, y=200)
await stx.browser.show_click_effect_async(page, x=100, y=200)
await stx.browser.inject_visual_effects_async(page)

# Console log collection
logs = stx.browser.collect_console_logs(page)
formatted = stx.browser.format_logs_devtools_style(logs)

# Failure capture
stx.browser.save_failure_artifacts(page, "test_name")

# Test monitoring with periodic screenshots
monitor = stx.browser.TestMonitor(page, interval=5.0)
```

## Key Features

- `SyncBrowserSession` / `sync_browser_session` — managed browser sessions preventing zombie processes
- Visual feedback: `show_cursor_at_async`, `show_click_effect_async`, `inject_visual_effects_async`
- `collect_console_logs` / `format_logs_devtools_style` — DevTools-style console capture
- `save_failure_artifacts` — capture screenshots and logs on test failure
- `TestMonitor` — periodic screenshot monitoring during tests
- All imports are optional (gracefully degrade if Playwright not installed)
