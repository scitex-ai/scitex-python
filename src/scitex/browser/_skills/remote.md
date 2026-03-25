---
description: ZenRowsAPIBrowser for cloud-based page rendering, screenshot capture, and anti-bot bypass via ZenRows API; ZenRowsBrowserManager wraps the Scraping Browser WebSocket service; CaptchaHandler solves Cloudflare/reCAPTCHA/hCaptcha challenges via 2Captcha.
---

# Remote Browser Services

These utilities delegate browser operations to external cloud services. They require API keys and optional Python packages (`aiohttp`).

---

## ZenRowsAPIBrowser

`scitex.browser.remote.ZenRowsAPIClient`

Browser-like interface that uses the ZenRows REST API to render pages, take screenshots, and bypass anti-bot measures. No local Chromium instance is needed.

```python
ZenRowsAPIBrowser(
    api_key: Optional[str] = None,  # Falls back to SCITEX_SCHOLAR_ZENROWS_API_KEY env var
    proxy_country: str = "au",      # Two-letter country code for proxy routing
    enable_antibot: bool = True,    # Enable ZenRows anti-bot bypass
    premium_proxy: bool = True,     # Use premium residential proxies
)
```

**Raises** `ValueError` if no API key is provided or found in environment.

### Key async method

```python
async def navigate_and_screenshot_async(
    self,
    url: str,
    screenshot_path: Optional[str] = None,
    wait_ms: int = 5000,
    js_instructions: Optional[List[Dict]] = None,
    return_html: bool = False,
) -> Dict[str, Any]
```

Navigates to `url` via the ZenRows API, waits `wait_ms` for JS rendering, optionally executes `js_instructions`, and optionally takes a screenshot.

Returns a dict with keys:
- `"html"` — rendered HTML (if `return_html=True`)
- `"screenshot"` — base64-encoded PNG (if `screenshot_path` is not None)
- `"screenshot_path"` — absolute path of saved screenshot file

### Environment variable

| Variable | Usage |
|----------|-------|
| `SCITEX_SCHOLAR_ZENROWS_API_KEY` | ZenRows API key |

### Example

```python
import asyncio
from scitex.browser.remote import ZenRowsAPIClient as ZenRowsAPIBrowser

async def fetch_rendered_page():
    browser = ZenRowsAPIBrowser(proxy_country="us")
    result = await browser.navigate_and_screenshot_async(
        url="https://target-with-antibot.com/article",
        screenshot_path="screenshot.png",
        return_html=True,
        wait_ms=5000,
    )
    print(result["html"][:500])

asyncio.run(fetch_rendered_page())
```

---

## ZenRowsBrowserManager

`scitex.browser.remote.ZenRowsBrowserManager`

Manages a WebSocket connection to the ZenRows Scraping Browser service (a cloud Chromium instance with built-in anti-bot bypass). Returns standard Playwright `Browser`, `BrowserContext`, and `Page` objects.

```python
ZenRowsBrowserManager(
    auth_manager=None,                    # Optional authentication manager for cookie injection
    zenrows_api_key: Optional[str] = ..., # Reads SCITEX_SCHOLAR_ZENROWS_API_KEY
    proxy_country: Optional[str] = ...,   # Reads SCITEX_SCHOLAR_ZENROWS_PROXY_COUNTRY
)
```

**Raises** `ValueError` if no API key is found.

The manager connects via WebSocket (`wss://browser.zenrows.com?apikey=...`). Because it returns real Playwright objects, all standard Playwright APIs work.

### Environment variables

| Variable | Usage |
|----------|-------|
| `SCITEX_SCHOLAR_ZENROWS_API_KEY` | ZenRows API key |
| `SCITEX_SCHOLAR_ZENROWS_PROXY_COUNTRY` | Default proxy country |

---

## CaptchaHandler

`scitex.browser.remote.CaptchaHandler`

Solves CAPTCHA challenges using the 2Captcha service.

```python
CaptchaHandler(
    api_key: Optional[str] = None,  # Falls back to SCITEX_SCHOLAR_2CAPTCHA_API_KEY
)
```

When no API key is configured, logs a warning and disables solving.

**Supported challenge types:**

- Cloudflare Turnstile
- Google reCAPTCHA v2 / v3
- hCaptcha

### Environment variable

| Variable | Usage |
|----------|-------|
| `SCITEX_SCHOLAR_2CAPTCHA_API_KEY` | 2Captcha API key |

### Usage pattern

```python
from scitex.browser.remote import CaptchaHandler
from playwright.async_api import async_playwright

async def handle_captcha_page():
    handler = CaptchaHandler()

    async with async_playwright() as pw:
        browser = await pw.chromium.launch(headless=False)
        page = await browser.new_page()
        await page.goto("https://site-with-captcha.com")

        # Detect and solve CAPTCHA if present
        # (method names depend on challenge type)
        await handler.solve_if_present_async(page)

        await browser.close()
```

---

## Choosing between local and remote browser

| Scenario | Recommended approach |
|----------|---------------------|
| General scraping with bot-detection concern | `BrowserMixin(mode="stealth")` + `StealthManager` |
| Heavy anti-bot protection (Cloudflare, etc.) | `ZenRowsAPIBrowser` or `ZenRowsBrowserManager` |
| CAPTCHA blocking the page | `CaptchaHandler` + 2Captcha API key |
| PDF capture of a public page | `save_as_pdf` (local, no API key needed) |
| Authenticated session requiring OAuth | `GoogleAuthHelper` + local Playwright |
