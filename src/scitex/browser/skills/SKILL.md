---
name: scitex-browser
description: Web page automation, PDF saving, and browser session management. Use when saving web pages as PDF, automating browser interactions, or managing browser sessions.
allowed-tools: mcp__scitex__browser_*
---

# Browser Automation with scitex.browser

## Quick Start

```python
from scitex.browser import save_as_pdf

# Save any web page as print-style PDF (cookie banners auto-dismissed)
save_as_pdf("https://nature.com/guidelines", "./guidelines.pdf")
```

## Common Workflows

### "Save a web page as PDF"

```python
from scitex.browser import save_as_pdf

# Basic usage
save_as_pdf("https://example.com", "./output.pdf")

# With options
save_as_pdf(
    "https://nature.com/nmeth/submission-guidelines",
    "./guidelines.pdf",
    wait_seconds=5,        # Wait for JS rendering
    format="A4",           # Paper format (A4, Letter, etc.)
    print_background=True, # Include background graphics
    margin_top="10mm",     # Page margins
)
```

### "Save page as PDF (async)"

```python
from scitex.browser import save_as_pdf_async

path = await save_as_pdf_async("https://example.com", "./output.pdf")
```

### "Interactive browser session (playwright-cli)"

For pages requiring login or complex navigation before saving:

```bash
# Requires: npm install -g @anthropic-ai/playwright-cli
playwright-cli open https://nature.com/paywall-article
playwright-cli fill e1 "user@example.com"     # login
playwright-cli fill e2 "password"
playwright-cli click e3                        # submit
playwright-cli pdf --filename=article.pdf      # save after auth
playwright-cli close
```

### "Open and control a browser session"

```bash
scitex browser open https://example.com           # Interactive mode
scitex browser open https://example.com --stealth  # Headless mode
scitex browser list                                # List sessions
scitex browser show <id>                           # Make visible
scitex browser hide <id>                           # Make headless
```

## CLI Commands

```bash
# Save page as PDF (automated, with cookie dismissal)
scitex browser save-as-pdf URL OUTPUT_PATH [OPTIONS]

# Options:
#   --wait-seconds FLOAT   Extra wait time for JS rendering (default: 3)
#   --no-background        Do not print background graphics
#   --format TEXT           Paper format: A4, Letter, etc. (default: A4)
#   --margin TEXT           Page margins: 10mm, 1in, etc. (default: 10mm)

# Examples:
scitex browser save-as-pdf https://example.com ./output.pdf
scitex browser save-as-pdf https://nature.com/guidelines ./g.pdf --wait-seconds 5
scitex browser save-as-pdf https://arxiv.org/abs/1234 ./paper.pdf --format Letter

# Browser session management
scitex browser open [URL] [--stealth] [--timeout N] [--background]
scitex browser list
scitex browser show [ID]
scitex browser hide [ID]
```

## MCP Tools (for AI agents)

| Tool | Purpose |
|------|---------|
| `browser_save_as_pdf` | Save a web page as print-style PDF |

## Python API

| Function | Purpose |
|----------|---------|
| `save_as_pdf(url, path, **opts)` | Save web page as PDF (sync) |
| `save_as_pdf_async(url, path, **opts)` | Save web page as PDF (async) |
| `detect_chrome_pdf_viewer_async(page)` | Detect Chrome's built-in PDF viewer |
| `click_download_for_chrome_pdf_viewer_async(page, path)` | Download PDF from Chrome viewer |

## Features

- **Auto cookie dismissal** — Consent banners removed before PDF capture
- **Overlay removal** — Fixed/sticky popups cleaned from page
- **Print-style PDF** — Uses Chromium's print-to-PDF (same as Ctrl+P → Save as PDF)
- **Configurable margins** — mm, in, cm units supported
- **Paper formats** — A4, Letter, Legal, Tabloid, etc.

## Installation

```bash
# Automated PDF saving (Python dependency)
pip install scitex[browser]   # Installs playwright>=1.40.0
playwright install chromium   # Download browser binary

# Interactive browser control (npm dependency, optional)
npm install -g @anthropic-ai/playwright-cli
```

## Dependencies

| Dependency | Type | Purpose |
|-----------|------|---------|
| `playwright>=1.40.0` | pip (required) | Chromium automation for PDF saving |
| `playwright-cli` | npm (optional) | Interactive browser control |
