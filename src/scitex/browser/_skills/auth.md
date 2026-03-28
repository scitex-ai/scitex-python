---
description: GoogleAuthHelper automates Google OAuth popup flows ("Continue with Google" button) for services that delegate authentication to Google; reads credentials from constructor args or GOOGLE_EMAIL / GOOGLE_PASSWORD env vars.
---

# Authentication

---

## GoogleAuthHelper

`scitex.browser.auth.GoogleAuthHelper`

Handles the popup-based Google OAuth 2.0 flow used by many web services.

```python
from scitex.browser.auth import GoogleAuthHelper

GoogleAuthHelper(
    email: Optional[str] = None,     # Falls back to GOOGLE_EMAIL env var
    password: Optional[str] = None,  # Falls back to GOOGLE_PASSWORD env var
    debug: bool = False,             # Also reads GOOGLE_AUTH_DEBUG env var
)
```

**Credential resolution order:** constructor argument → environment variable → empty string.

### Methods

```python
async def login_via_google_button(
    self,
    page: Page,
    google_button_selector: str = 'button:has-text("Continue with Google")',
    timeout: int = 60000,
) -> bool
```

Performs a complete Google OAuth flow:

1. Clicks the "Continue with Google" button on the main page.
2. Waits for the Google authentication popup to open.
3. Fills in the email address and clicks Next.
4. Fills in the password and clicks Next.
5. Waits for the popup to close and the original page to reflect the authenticated state.

Returns `True` on success, `False` otherwise.

**Parameters**

| Parameter | Default | Description |
|-----------|---------|-------------|
| `page` | required | The main Playwright `Page` containing the Google button |
| `google_button_selector` | `'button:has-text("Continue with Google")'` | CSS / text selector for the Google login button |
| `timeout` | `60000` | Maximum milliseconds to wait for the complete flow |

### Environment variables

| Variable | Usage |
|----------|-------|
| `GOOGLE_EMAIL` | Default email when not passed to constructor |
| `GOOGLE_PASSWORD` | Default password when not passed to constructor |
| `GOOGLE_AUTH_DEBUG` | Set to any truthy string to enable debug output to stderr |

### Example

```python
import asyncio
from playwright.async_api import async_playwright
from scitex.browser.auth import GoogleAuthHelper

async def login_to_service():
    auth = GoogleAuthHelper(
        email="researcher@gmail.com",
        password="my_password",
        debug=True,
    )

    async with async_playwright() as pw:
        browser = await pw.chromium.launch(headless=False)
        page = await browser.new_page()

        await page.goto("https://service.example.com/login")

        success = await auth.login_via_google_button(
            page,
            google_button_selector='button:has-text("Sign in with Google")',
        )

        if success:
            print("Authenticated successfully")
        else:
            raise RuntimeError("Google OAuth flow failed")

        # Continue with authenticated session
        content = await page.content()
        await browser.close()

asyncio.run(login_to_service())
```

### Using env vars (no credentials in code)

```bash
export GOOGLE_EMAIL="researcher@gmail.com"
export GOOGLE_PASSWORD="my_password"
```

```python
auth = GoogleAuthHelper()  # reads from env
success = await auth.login_via_google_button(page)
```

### Notes

- The Google OAuth popup is a separate browser window. `login_via_google_button` uses `page.expect_popup()` to handle it.
- Two-factor authentication (2FA) is not handled; use an account with 2FA disabled for automation.
- For headless Chromium, Google may block the flow. Run with `headless=False` or use a persistent context with saved cookies.
