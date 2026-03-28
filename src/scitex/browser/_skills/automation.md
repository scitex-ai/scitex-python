---
description: CookieAutoAcceptor injects a self-contained JavaScript polling loop into browser contexts to automatically dismiss cookie consent banners; also provides programmatic async acceptance and banner-presence checking.
---

# Automation Utilities

---

## CookieAutoAcceptor

`scitex.browser.automation.CookieAutoAcceptor`

Handles cookie consent banners automatically. The primary mechanism is a JavaScript init script injected into a browser context before any page loads, so banners are dismissed the moment they appear.

```python
CookieAutoAcceptor()
```

### Configured cookie-button text

Exact text-match (case-insensitive) on `<button>` and `<a>` elements:

```
"Accept all cookies", "Accept All", "Accept cookies", "Accept",
"I Accept", "OK", "Continue", "Agree",
"Continue without an account", "Don't ask again"
```

### Configured CSS selectors

```
[data-testid*='accept'], [id*='accept'], [class*='accept'],
button[aria-label*='Accept'], .cookie-banner button:first-of-type,
#cookie-banner button:first-of-type
```

### Methods

```python
def get_auto_acceptor_script(self) -> str
    # Returns a JavaScript IIFE string to pass to context.add_init_script().
    # The script polls once per second for up to 30 seconds.
    # Skips any element with data-scitex-no-auto-click, id "stop-automation-btn",
    # or any id containing "scitex".
    # Clicks the first visible matching button/link, then cancels the interval.

async def inject_auto_acceptor_async(self, context) -> None
    # Deprecated convenience wrapper around get_auto_acceptor_script().
    # Use context.add_init_script(acceptor.get_auto_acceptor_script()) directly.

async def check_cookie_banner_exists_async(self, page: Page) -> bool
    # Returns True if an element matching ".cookie-banner, [class*='cookie']"
    # is currently visible on the page.
```

### Usage — context-level (recommended)

Inject the script once at context creation. All pages opened from this context will have banners dismissed automatically.

```python
from playwright.async_api import async_playwright
from scitex.browser.automation import CookieAutoAcceptor

acceptor = CookieAutoAcceptor()

async with async_playwright() as pw:
    browser = await pw.chromium.launch(headless=False)
    context = await browser.new_context()
    await context.add_init_script(acceptor.get_auto_acceptor_script())

    page = await context.new_page()
    await page.goto("https://www.springer.com")
    # Cookie banner dismissed automatically within ~1 second of page load
```

### Usage — BrowserMixin integration

`BrowserMixin.new_page()` and `BrowserMixin.create_browser_context_async()` both call `context.add_init_script(self.cookie_acceptor.get_auto_acceptor_script())` automatically. No additional setup is needed when using `BrowserMixin` subclasses.

```python
class MyScraper(BrowserMixin):
    pass

async with MyScraper(mode="stealth") as scraper:
    page = await scraper.new_page("https://www.springer.com")
    # Cookie banner is handled automatically
```

### Post-load check

```python
banner_visible = await acceptor.check_cookie_banner_exists_async(page)
if banner_visible:
    # Script may not have matched — try PopupHandler as fallback
    from scitex.browser import close_popups_async
    await close_popups_async(page)
```

### Script behaviour summary

| Aspect | Detail |
|--------|--------|
| Polling interval | 1000 ms |
| Max duration | 30 seconds |
| Stop condition | First successful click |
| Skipped elements | `data-scitex-no-auto-click`, `id="stop-automation-btn"`, `id` contains `"scitex"` |
| Visibility check | `element.offsetParent !== null` |
| Match priority | Text-based first, then CSS selectors |
