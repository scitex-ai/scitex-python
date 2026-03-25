---
name: browser-debugging
description: Visual browser debugging utilities — browser_logger for in-page overlay messages with screenshot capture, show_grid_async, highlight_element_async, visual cursor/click effects, failure capture fixtures for pytest, TestMonitor for periodic screenshots, SyncBrowserSession for zombie-free test sessions.
---

# Debugging Tools

All utilities are in `scitex.browser.debugging` (re-exported from `scitex.browser`).

---

## browser_logger

A singleton `BrowserLogger` instance. Its methods inject stacking popup messages into the live page and optionally take timestamped screenshots.

```python
from scitex.browser import browser_logger

await browser_logger.debug(page, message, ...)
await browser_logger.info(page, message, ...)
await browser_logger.success(page, message, ...)
await browser_logger.warning(page, message, ...)
await browser_logger.error(page, message, ...)
```

All methods call the underlying `log_page_async`:

```python
async def log_page_async(
    page,
    message: str,
    duration_ms: int = 60_000,
    take_screenshot: bool = True,
    screenshot_dir: Path | str = None,
    verbose: bool = True,
    level: str = "info",
    func_name: str = "BrowserLogger",
)
```

**Behaviour**

- Injects a coloured popup banner into the page at the top-right corner.
- Banners persist for `duration_ms` ms (default 60 s) and stack vertically.
- Banners survive page navigations (re-injected on `framenavigated` event).
- Stack is capped at 10 items; oldest messages are removed first.
- Takes a screenshot and saves it to `$SCITEX_DIR/browser/screenshots/{category}/{timestamp}_{message}.png` when `take_screenshot=True`.
- A brief flash effect marks the screenshot moment visually.

**Popup colours by level**

| Level | Colour |
|-------|--------|
| `debug` | Grey `#6C757D` |
| `info` | Cyan `#17A2B8` |
| `success` | Green `#28A745` |
| `warning` | Yellow `#FFC107` |
| `error` / `fail` | Red `#DC3545` |

**Example**

```python
from scitex.browser import browser_logger

await browser_logger.debug(page, "Navigating to article page...")
await page.goto("https://example.com/article")
await browser_logger.success(page, "Page loaded", take_screenshot=True)
```

---

## show_grid_async

```python
async def show_grid_async(page) -> None
```

Overlays a coordinate grid on the page. Useful for visually locating elements when computing pixel positions for `mouse.click`.

---

## highlight_element_async

```python
async def highlight_element_async(page, selector: str) -> None
```

Draws a bright border around the element matched by `selector`. Useful for confirming that a CSS selector targets the intended element.

---

## Visual cursor and click effects

Inject CSS-animated UI into the page for visual test feedback. Available as both sync (`Page`) and async (`Page`) variants.

```python
# Inject base CSS (call once per page; idempotent)
inject_visual_effects(page)                    # sync
await inject_visual_effects_async(page)        # async

# Show a red cursor circle at (x, y)
show_cursor_at(page, x, y)
await show_cursor_at_async(page, x, y)

# Show a ripple effect at (x, y)
show_click_effect(page, x, y)
await show_click_effect_async(page, x, y)

# Display a step progress message overlay
show_step(page, message: str, step: int, total: int)
await show_step_async(page, message, step, total)

# Display a test result badge (pass/fail)
show_test_result(page, passed: bool, message: str = "")
await show_test_result_async(page, passed, message)
```

Visual elements are injected as fixed-position DOM nodes with z-index 2147483647 (maximum). They are non-interactive (`pointer-events: none`).

---

## Failure capture fixtures

Automatic artifact collection for pytest-playwright E2E tests.

```python
from scitex.browser.debugging import (
    setup_console_interceptor,
    collect_console_logs,
    collect_console_logs_detailed,
    format_logs_devtools_style,
    save_failure_artifacts,
    create_failure_capture_fixture,
)
```

### setup_console_interceptor

```python
async def setup_console_interceptor(page) -> None
```

Injects a JavaScript console interceptor that mirrors `console-interceptor.ts` from scitex-cloud. Captures log level, message, source file, and line number for every `console.log/info/warn/error/debug` call. Stores up to 2000 entries in `window._scitex_console_history`.

### collect_console_logs

```python
async def collect_console_logs(page) -> List[Dict]
```

Returns the list of captured log entries from the injected interceptor.

### collect_console_logs_detailed

```python
async def collect_console_logs_detailed(page) -> List[Dict]
```

Like `collect_console_logs` but includes stack trace information per entry.

### format_logs_devtools_style

```python
def format_logs_devtools_style(logs: List[Dict]) -> str
```

Formats the log list as a DevTools-style string for test failure output.

### save_failure_artifacts

```python
async def save_failure_artifacts(page, test_name: str, output_dir: Path | str)
```

On test failure: saves a screenshot and the full page HTML to `output_dir/{test_name}_screenshot.png` and `{test_name}_page.html`.

### create_failure_capture_fixture

```python
def create_failure_capture_fixture(output_dir: str = "test_artifacts")
```

Factory that returns a pytest fixture function. Integrate in `conftest.py`:

```python
# conftest.py
from scitex.browser.debugging import create_failure_capture_fixture

capture_failure = create_failure_capture_fixture("test_artifacts")
```

---

## TestMonitor

Periodic screenshot capture during E2E test execution.

```python
class TestMonitor:
    def __init__(
        self,
        output_dir: str | Path = None,  # default: $SCITEX_DIR/test_monitor
        interval: float = 2.0,          # seconds between screenshots
        quality: int = 70,              # JPEG quality 1-100
        verbose: bool = False,
        test_name: str = None,
    )
```

```python
def start(self, test_name: str = None) -> str  # returns session_id
def stop(self) -> None
def create_gif(self) -> Optional[str]           # returns GIF path
```

### Fixture helpers

```python
def create_test_monitor_fixture(
    interval: float = 2.0,
    verbose: bool = False,
)
# Returns a pytest fixture that starts/stops monitoring automatically.

@contextmanager
def monitor_test(test_name: str, interval: float = 2.0):
    # Context manager for one-off test monitoring.
```

**conftest.py example**

```python
from scitex.browser.debugging import create_test_monitor_fixture

test_monitor = create_test_monitor_fixture(interval=2.0, verbose=True)
```

---

## SyncBrowserSession

Context manager that ensures no zombie Playwright processes are left after sync (pytest-playwright) E2E tests.

```python
class SyncBrowserSession:
    def __init__(
        self,
        page: Page,
        timeout: int = 60,
        on_enter: Optional[Callable[[Page], None]] = None,
        on_exit: Optional[Callable[[Page, bool], None]] = None,
    )
```

Tracks browser PIDs at `__enter__` and kills orphaned processes at `__exit__`. Registers an `atexit` handler for emergency cleanup on crash.

**Class-level tracking**

```python
SyncBrowserSession._active_sessions  # List of all open sessions
```

### Usage

```python
# conftest.py
from scitex.browser import SyncBrowserSession

@pytest.fixture
def browser_session(page):
    with SyncBrowserSession(page) as session:
        yield session
```

### Fixture factory

```python
def create_browser_session_fixture(
    timeout: int = 60,
    on_enter=None,
    on_exit=None,
)
# Returns a pytest fixture function.
```

```python
# conftest.py
from scitex.browser import create_browser_session_fixture

browser_session = create_browser_session_fixture()
```

### Context manager (non-pytest)

```python
from scitex.browser import sync_browser_session  # @contextmanager

with sync_browser_session(page) as session:
    page.goto("https://example.com")
```
