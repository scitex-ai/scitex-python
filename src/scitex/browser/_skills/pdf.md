---
description: Save any URL as a print-style PDF (save_as_pdf / save_as_pdf_async) with cookie-banner dismissal; detect Chrome's built-in PDF viewer (detect_chrome_pdf_viewer_async); click the viewer's download button (click_download_for_chrome_pdf_viewer_async).
---

# PDF Utilities

---

## save_as_pdf / save_as_pdf_async

```python
async def save_as_pdf_async(
    url: str,
    output_path: str,
    *,
    wait_seconds: float = 3,
    print_background: bool = True,
    format: str = "A4",
    margin_top: str = "10mm",
    margin_bottom: str = "10mm",
    margin_left: str = "10mm",
    margin_right: str = "10mm",
) -> str

def save_as_pdf(url: str, output_path: str, **kwargs) -> str
    # Synchronous wrapper: asyncio.run(save_as_pdf_async(...))
```

Navigates to `url` (adds `https://` if no scheme), waits for `networkidle`, sleeps `wait_seconds` extra for JS rendering, dismisses cookie consent banners and large fixed/sticky overlays, then calls `page.pdf()` (Playwright print-style, headless Chromium).

Returns the absolute path of the saved PDF.

**Raises** `RuntimeError` if the PDF was not created or is smaller than 1 KB.

**Parameters**

| Parameter | Default | Description |
|-----------|---------|-------------|
| `url` | required | Full URL or bare domain |
| `output_path` | required | Destination path; `.pdf` extension appended if missing |
| `wait_seconds` | `3` | Extra sleep after `networkidle` for heavy SPA pages |
| `print_background` | `True` | Include CSS background graphics |
| `format` | `"A4"` | Paper format (`"A4"`, `"Letter"`, `"A3"`, etc.) |
| `margin_*` | `"10mm"` | CSS margin strings (`"10mm"`, `"1in"`, `"0"`) |

**Example — sync**

```python
from scitex.browser import save_as_pdf

path = save_as_pdf("https://example.com", "~/docs/example.pdf")
print(f"Saved: {path}")
```

**Example — async**

```python
from scitex.browser import save_as_pdf_async

path = await save_as_pdf_async(
    "https://www.nature.com/articles/s41586-024-00001-0",
    "article.pdf",
    wait_seconds=5,
    format="A4",
)
```

**MCP tool**

```
mcp__scitex__browser_save_as_pdf
```

### Overlay dismissal details

`_dismiss_overlays` runs before PDF capture:

1. Iterates a list of ~14 cookie-consent selectors; clicks the first visible one.
2. Runs JavaScript that removes fixed/sticky elements occupying more than 30% of the viewport in either dimension (covers banners, sticky headers, GDPR overlays).

---

## detect_chrome_pdf_viewer_async

```python
async def detect_chrome_pdf_viewer_async(
    page,
    verbose: bool = False,
    func_name: str = "detect_chrome_pdf_viewer_async",
) -> bool
```

Returns `True` if a Chrome PDF viewer is loaded on the current page. Uses six detection methods in JavaScript:

1. `embed[type="application/pdf"]`
2. `iframe[src*=".pdf"]`
3. `object[type="application/pdf"]`
4. `window.PDFViewerApplication` (Chrome built-in viewer)
5. `[data-testid="pdf-viewer"]`
6. `navigator.mimeTypes["application/pdf"]`
7. IEEE-specific selectors: `#pdfViewer`, `.pdf-viewer`, `[id*="pdf"]`
8. `document.contentType === "application/pdf"`

**Important:** The caller should call `page.wait_for_load_state("networkidle")` _before_ calling this function. It intentionally does not wait internally to avoid redundant waits.

**Example**

```python
from scitex.browser import detect_chrome_pdf_viewer_async

await page.goto(pdf_url)
await page.wait_for_load_state("networkidle", timeout=15000)

if await detect_chrome_pdf_viewer_async(page, verbose=True):
    print("PDF viewer is active")
```

---

## click_download_for_chrome_pdf_viewer_async

```python
async def click_download_for_chrome_pdf_viewer_async(
    page,
    output_path: Path | str,
    verbose: bool = False,
    func_name: str = "click_download_for_chrome_pdf_viewer_async",
) -> bool
```

Clicks the download button in Chrome's built-in PDF viewer (located at approximately 95% x, 3% y of the viewport), waits up to 120 seconds for the download to start, saves the file to `output_path`, and verifies the result is larger than 1 KB.

Returns `True` on success, `False` otherwise.

**Parameters**

| Parameter | Description |
|-----------|-------------|
| `page` | Playwright Page showing a PDF in Chrome's PDF viewer |
| `output_path` | Destination path; `.pdf` extension appended if missing |
| `verbose` | Emit overlay log messages via `browser_logger` |

**Timing**

- `expect_download` timeout: 120 seconds
- Post-download pause: 2 seconds

**Example**

```python
from scitex.browser import (
    detect_chrome_pdf_viewer_async,
    click_download_for_chrome_pdf_viewer_async,
)

await page.goto("https://publisher.com/article/pdf/12345")
await page.wait_for_load_state("networkidle")

if await detect_chrome_pdf_viewer_async(page):
    success = await click_download_for_chrome_pdf_viewer_async(
        page,
        "paper_12345.pdf",
        verbose=True,
    )
    if not success:
        raise RuntimeError("PDF download failed")
```

---

## Choosing the right function

| Scenario | Use |
|----------|-----|
| Capture any public web page as a formatted PDF | `save_as_pdf` / `save_as_pdf_async` |
| Check if a page has loaded a PDF file in Chrome's viewer | `detect_chrome_pdf_viewer_async` |
| Download a PDF that is already open in Chrome's PDF viewer | `click_download_for_chrome_pdf_viewer_async` |
