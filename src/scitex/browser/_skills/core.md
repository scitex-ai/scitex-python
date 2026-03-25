---
description: BrowserMixin for shared async Chromium instances with interactive/stealth modes and multi-tab management; ChromeProfileManager for Chrome extension installation, status checking, and profile rsync.
---

# Core Browser Infrastructure

## BrowserMixin

`scitex.browser.core.BrowserMixin`

Base mixin that manages a shared Chromium instance and a list of pages. Intended to be subclassed.

```python
class BrowserMixin:
    def __init__(self, mode: str)  # mode: "interactive" | "stealth"
```

### Mode semantics

| Mode | Viewport | headless |
|------|----------|---------|
| `"interactive"` | 1280 x 720 (human-friendly) | False |
| `"stealth"` | controlled by `StealthManager` | False |

Both modes launch Chromium non-headlessly. Visibility is determined by the viewport, not the headless flag. The `get_browser_async` method passes an extended set of stealth Chrome flags regardless of mode.

### Key async methods

```python
async def get_browser_async(self) -> Browser
    # Returns the shared Browser, creating it if needed.

async def new_page(self, url: str = None) -> Page
    # Creates a new BrowserContext, injects the CookieAutoAcceptor init script,
    # opens a page, and optionally navigates to url (wait_until="domcontentloaded",
    # timeout=30000). Appends to self.contexts and self.pages.

async def close_page(self, page_index: int)
    # Closes the context + page at the given list index.

async def close_all_pages(self)
    # Closes all open contexts and pages.

async def create_browser_context_async(self, playwright_instance, **context_options)
    # Launches a browser, creates a context with cookie auto-acceptance, and
    # returns (browser, context). Mode determines headless: stealth=True, interactive=False.

async def get_session_async(self, timeout: int = 30) -> aiohttp.ClientSession
    # Returns a cached aiohttp.ClientSession.

async def close_session(self)
    # Closes the aiohttp session.

async def accept_cookies_async(self, page_index: int = 0, wait_seconds: int = 2)
    # Manually trigger cookie acceptance on the page at page_index.

async def show_async(self) -> BrowserMixin
    # Switch to interactive mode; recreates all existing pages at their current URLs.

async def hide_async(self) -> BrowserMixin
    # Switch to stealth mode; recreates all existing pages at their current URLs.
```

### Sync mode helpers (non-async)

```python
def interactive(self) -> BrowserMixin  # Set mode to "interactive" (resets shared browser)
def stealth(self) -> BrowserMixin      # Set mode to "stealth" (resets shared browser)
```

### Class-level shared state

```python
BrowserMixin._shared_browser     # Shared Browser instance (class variable)
BrowserMixin._shared_playwright  # Shared Playwright instance (class variable)

@classmethod
async def get_shared_browser_async(cls) -> Browser   # Deprecated; use get_browser_async()
@classmethod
async def cleanup_shared_browser_async(cls)           # Call on app shutdown
```

### Context manager

```python
async with DemoBrowser(mode="interactive") as b:
    page = await b.new_page("https://example.com")
    content = await page.content()
# Calls close_all_pages() and close_session() on exit
```

### Subclassing example

```python
from scitex.browser.core import BrowserMixin

class MyScraper(BrowserMixin):
    async def scrape_async(self, url: str) -> str:
        page = await self.new_page(url)
        return await page.content()

async def main():
    async with MyScraper(mode="stealth") as scraper:
        html = await scraper.scrape_async("https://example.com")
        print(f"Fetched {len(html)} bytes")
```

---

## ChromeProfileManager

`scitex.browser.core.ChromeProfileManager`

Manages Chrome user-data profiles, with emphasis on browser extensions needed for automated literature search.

```python
ChromeProfileManager(profile_name: str, config: Optional[ScholarConfig] = None)
```

**profile_name** can be any string; typical built-in names are `"system"`, `"extension"`, `"auth"`, `"stealth"`, plus dynamic names like `"worker_0"` for parallel workflows.

### Tracked extensions

| Key | Extension name |
|-----|---------------|
| `zotero_connector` | Zotero Connector |
| `lean_library` | Lean Library |
| `popup_blocker` | Pop-up Blocker |
| `accept_cookies` | Accept all cookies |
| `2captcha_solver` | 2Captcha Solver |
| `captcha_solver` | CAPTCHA Solver |

### Key methods

```python
def check_extensions_installed(
    self,
    profile_dir: Path = None,
    verbose: bool = True,
) -> bool
    # Returns True if all 6 extensions have manifest.json installed.
    # Logs warnings per missing extension when verbose=True.

def get_extension_args(self) -> list[str]
    # Returns a list of Chrome CLI flags for --load-extension, --disable-extensions-except,
    # --enable-extensions, --disable-extensions-file-access-check, --disable-web-security.
    # Provide this list as extra_args when launching Chromium via Playwright.

async def install_extensions_manually_if_not_installed_async(
    self,
    verbose: bool = False,
) -> bool
    # If extensions are missing, launches Chrome with extension store URLs open,
    # waits for the user to press Enter, then verifies installation.

async def handle_runtime_extension_dialogs_async(self, page) -> bool
    # Clicks common consent dialog buttons (Agree, Accept, Continue, OK, etc.)
    # that may appear after extension load.

def sync_from_profile(self, source_profile_name: str = "system") -> bool
    # Uses rsync -auv --delete to copy the source profile into self.profile_dir.
    # Tolerates rsync exit code 23 with only "failed to set times" errors (WSL).
    # Returns True on success.
```

### Usage example

```python
from scitex.browser.core import ChromeProfileManager
from playwright.async_api import async_playwright

manager = ChromeProfileManager("extension")

# Get Playwright launch args that load installed extensions
ext_args = manager.get_extension_args()

async with async_playwright() as pw:
    browser = await pw.chromium.launch_persistent_context(
        user_data_dir=str(manager.profile_dir),
        headless=False,
        args=ext_args,
    )
    page = await browser.new_page()
    await manager.handle_runtime_extension_dialogs_async(page)
    # ...
    await browser.close()
```

### Profile sync

```python
# Copy system profile (with all manually installed extensions) to a worker profile
worker = ChromeProfileManager("worker_0")
worker.sync_from_profile("system")  # rsync system → worker_0
```
