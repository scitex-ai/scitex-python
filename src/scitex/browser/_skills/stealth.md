---
description: StealthManager provides randomised user-agents, viewports, and HTTP headers to reduce bot-detection fingerprinting; HumanBehavior simulates human timing delays, natural multi-step mouse movement, hover-before-click, and reading pauses.
---

# Stealth and Anti-Bot

---

## StealthManager

`scitex.browser.stealth.StealthManager`

Generates randomised browser context options designed to avoid bot-detection fingerprinting.

```python
StealthManager(
    viewport_size: tuple = None,   # Fixed (width, height); overrides random selection
    spoof_dimension: bool = False, # If True and viewport_size not set, uses 1920x1080
)
```

### Methods

```python
def get_random_user_agent(self) -> str
    # Returns a randomly selected User-Agent string from a curated list.
    # Currently includes Chrome 138 on Linux x86_64.

def get_random_viewport(self) -> dict
    # Returns {"width": ..., "height": ...}.
    # Priority: viewport_size > spoof_dimension (1920x1080) > random choice.
    # Random pool: 1920x1080, 1366x768, 1440x900, 1280x720.

def get_stealth_options(self) -> dict
    # Returns a dict suitable for browser.new_context(**options).
    # Includes: viewport, user_agent, extra_http_headers (Accept, Accept-Language, etc.).
```

### get_stealth_options output shape

```python
{
    "viewport": {"width": 1920, "height": 1080},
    "user_agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 ...",
    "extra_http_headers": {
        "Accept": "text/html,application/xhtml+xml,...",
        "Accept-Language": "en-US,en;q=0.9",
        # ...
    }
}
```

### Usage with Playwright

```python
from playwright.async_api import async_playwright
from scitex.browser.stealth import StealthManager

stealth = StealthManager()
opts = stealth.get_stealth_options()

async with async_playwright() as pw:
    browser = await pw.chromium.launch(headless=False)
    context = await browser.new_context(**opts)
    page = await context.new_page()
    await page.goto("https://target.com")
```

### Usage with BrowserMixin

`BrowserMixin.get_browser_async()` always applies a fixed set of anti-automation Chrome flags (see `core.md`). For per-context randomisation, combine with `StealthManager.get_stealth_options()`:

```python
browser = await my_mixin.get_browser_async()
context = await browser.new_context(**stealth.get_stealth_options())
```

---

## HumanBehavior

`scitex.browser.stealth.HumanBehavior`

Simulates human-like interaction patterns to avoid timing-based bot detection.

```python
HumanBehavior()
```

### Methods

```python
async def random_delay_async(
    self,
    min_ms: int = 1000,
    max_ms: int = 3000,
    page: Page = None,
) -> None
    # Sleeps for a random duration in [min_ms, max_ms].
    # If page is provided, logs a debug overlay message.

async def reading_delay_async(
    self,
    content_length: int = 1000,
    page: Page = None,
) -> None
    # Simulates reading time based on content length.
    # Formula: (content_length / 5 words) / 250 wpm * 60000 ms.
    # Clamped to [2000, 10000] ms, then multiplied by a uniform [0.8, 1.2] factor.

async def mouse_move_async(
    self,
    page: Page,
    x: Optional[int] = None,
    y: Optional[int] = None,
) -> None
    # Moves the mouse to (x, y) using 3-7 intermediate steps along an
    # ease-in-out (smoothstep) curve.
    # Defaults: x in [100, 1200], y in [100, 800].

async def hover_and_click_async(
    self,
    page: Page,
    selector: str = None,
    element=None,
) -> None
    # Moves mouse to element, pauses briefly, then clicks.
    # Accepts either a CSS selector or a resolved element handle.
```

### Example

```python
from scitex.browser.stealth import HumanBehavior

human = HumanBehavior()

# Realistic page interaction sequence
await human.random_delay_async(500, 1500, page=page)
await human.mouse_move_async(page, x=640, y=400)
await human.hover_and_click_async(page, selector="button.submit")
await human.reading_delay_async(content_length=3000, page=page)
```

### Combining with interaction helpers

```python
from scitex.browser import fill_with_fallbacks_async
from scitex.browser.stealth import HumanBehavior

human = HumanBehavior()

await human.random_delay_async(300, 800)
await fill_with_fallbacks_async(page, "#email", "user@example.com")
await human.random_delay_async(200, 600)
await fill_with_fallbacks_async(page, "#password", "secret")
await human.random_delay_async(500, 1000)
await human.hover_and_click_async(page, "#login-button")
```
