---
description: Robust element clicking and form filling with three-level fallback strategies; popup/cookie banner detection and dismissal via PopupHandler, close_popups_async, ensure_no_popups_async; viewport-center clicking via click_center_async.
---

# Interaction Helpers

All functions are async and accept a Playwright `Page` object.

---

## click_with_fallbacks_async

```python
async def click_with_fallbacks_async(
    page: Page,
    selector: str,
    method: str = "auto",
    verbose: bool = False,
) -> bool
```

Attempts to click `selector` using up to three strategies in order.

| `method` value | Strategy sequence |
|---------------|-------------------|
| `"auto"` | playwright → force → js |
| `"playwright"` | `page.click(selector, timeout=5000)` only |
| `"force"` | `page.click(selector, force=True, timeout=5000)` only |
| `"js"` | `document.querySelector(selector).click()` only |

Returns `True` on first success; logs an error and returns `False` if all attempts fail.

When `verbose=True`, emits overlay messages via `browser_logger` for each attempt outcome.

**Example**

```python
from scitex.browser import click_with_fallbacks_async

success = await click_with_fallbacks_async(page, "button.submit")
if not success:
    raise RuntimeError("Could not click submit button")
```

---

## fill_with_fallbacks_async

```python
async def fill_with_fallbacks_async(
    page: Page,
    selector: str,
    value: str,
    method: str = "auto",
    verbose: bool = False,
) -> bool
```

Fills an input element with `value` using up to three strategies.

| `method` value | Strategy sequence |
|---------------|-------------------|
| `"auto"` | playwright → type → js |
| `"playwright"` | `page.fill(selector, value, timeout=5000)` |
| `"type"` | Click, Ctrl+A, then `page.type(selector, value, delay=50)` |
| `"js"` | Set `.value` and dispatch `input`/`change` events |

Returns `True` on first success, `False` if all fail.

**Example**

```python
from scitex.browser import fill_with_fallbacks_async

ok = await fill_with_fallbacks_async(
    page,
    "textarea[name='q']",
    "SciTeX browser automation",
)
```

---

## click_center_async

```python
async def click_center_async(
    page,
    verbose: bool = False,
    func_name: str = "click_center_async",
) -> Any
```

Clicks the pixel at the exact center of `page.viewport_size`, then waits 1000 ms.

Useful for dismissing overlays or focusing the page when no specific element can be targeted.

**Example**

```python
from scitex.browser import click_center_async

await click_center_async(page, verbose=True)
```

---

## PopupHandler

`scitex.browser.interaction.PopupHandler`

Class that detects and closes various popup types on a page.

```python
PopupHandler(page: Page)
```

### Detection

```python
async def detect_popups(self) -> List[Dict]
```

Returns a list of visible popup descriptors sorted by CSS `z-index` (highest first). Each entry has:

```python
{
    "selector": str,    # matched CSS selector
    "type": str,        # "cookie" | "newsletter" | "auth" | "ai_promotion" | "unknown"
    "text": str,        # first 200 chars of element text
    "zIndex": str,
    "position": {"top": ..., "left": ..., "width": ..., "height": ...}
}
```

Inspected selectors include `.modal`, `.overlay`, `[role="dialog"]`, `.popup`, `#onetrust-banner-sdk`, `[class*="modal"]`, and more.

### Handling

```python
async def handle_cookie_popup(self) -> bool
    # Clicks the first visible button matching COOKIE_SELECTORS.
    # Skips elements with data-scitex-no-auto-click attribute.

async def close_popup(self, popup_info: Optional[Dict] = None) -> bool
    # Tries CLOSE_SELECTORS in order. Falls back to pressing Escape.

async def handle_all_popups(
    self,
    max_attempts: int = 3,
    delay_ms: int = 1000,
) -> int
    # Runs detect_popups → handle_cookie_popup / close_popup in a loop.
    # Returns the total number of popups handled.

async def wait_and_handle_popups(self, timeout_ms: int = 5000) -> int
    # Polls for popups until timeout_ms elapses, handling each one found.
```

`handler.handled_popups` — list of `(strategy, selector)` tuples for each handled popup.

### Convenience functions

```python
async def close_popups_async(
    page: Page,
    handle_cookies: bool = True,
    close_others: bool = True,
    max_attempts: int = 3,
    wait_first: bool = True,
    wait_ms: int = 2000,
) -> Tuple[int, List]
    # Creates a PopupHandler, optionally waits wait_ms for popups to appear,
    # then calls handle_all_popups. Returns (count_handled, handled_popups_list).

async def ensure_no_popups_async(
    page: Page,
    check_interval_ms: int = 1000,
) -> bool
    # Calls detect + handle up to 3 times. Returns True if page is popup-free.
```

**Example**

```python
from scitex.browser import close_popups_async, ensure_no_popups_async, PopupHandler

await page.goto("https://www.springer.com")

# Quick convenience approach
count, handled = await close_popups_async(page, wait_ms=3000)
print(f"Dismissed {count} popup(s)")

# Class-based approach for more control
handler = PopupHandler(page)
popups = await handler.detect_popups()
for p in popups:
    print(p["type"], p["text"][:60])
await handler.handle_all_popups()

# Verify clear before proceeding
assert await ensure_no_popups_async(page)
```

### SciTeX button protection

PopupHandler and CookieAutoAcceptor both skip elements that carry:
- `data-scitex-no-auto-click` attribute
- `id="stop-automation-btn"` or any id containing `"scitex"`
- parent with `data-scitex-no-auto-click`

This prevents automation from accidentally clicking SciTeX's own interactive overlay buttons.
