# playwright-cli Integration

## When to Use

Use `playwright-cli` (interactive) when:
- Page requires login/authentication before saving
- Need to navigate complex SPAs before capturing
- Want to inspect page state (snapshots, console logs)

Use `save_as_pdf` (automated) when:
- Page is publicly accessible
- No interaction needed before saving
- Running in scripts or via MCP tools

## Installation

```bash
npm install -g @anthropic-ai/playwright-cli
```

## Interactive PDF Workflow

```bash
# 1. Open browser
playwright-cli open https://example.com

# 2. Handle auth if needed
playwright-cli fill e1 "user@example.com"
playwright-cli fill e2 "password"
playwright-cli click e3

# 3. Navigate to target page
playwright-cli goto https://example.com/protected-content

# 4. Save as PDF
playwright-cli pdf --filename=content.pdf

# 5. Close
playwright-cli close
```

## Checking Availability

```python
from scitex.browser import is_playwright_cli_available

if is_playwright_cli_available():
    # Can use interactive mode
    pass
```
