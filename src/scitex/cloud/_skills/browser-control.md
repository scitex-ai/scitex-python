---
description: Evaluate JavaScript in the user's browser and drive UI interactions with eval_js() and ui_action().
---

# Browser Control

## eval_js

Evaluates a JavaScript expression or statement in the user's connected browser and returns the result.

```python
eval_js(code: str, timeout: int = 10, **kw) -> dict
```

**Parameters**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `code` | `str` | required | JavaScript code to evaluate in the browser. |
| `timeout` | `int` | `10` | Seconds to wait for the result before raising. |
| `**kw` | any | — | Forwarded to `CloudClient.__init__`. |

**Returns:** `dict` — result of the JavaScript evaluation as returned by `scitex_cloud`.

**Implementation:** `_Client(**kw).eval_js(code, timeout)`

### Examples

```python
import scitex as stx

# Read the page title
result = stx.cloud.eval_js("document.title")

# Get current URL
result = stx.cloud.eval_js("window.location.href")

# Read a DOM element's text
result = stx.cloud.eval_js("document.querySelector('#status').innerText")

# Execute multi-line JS
result = stx.cloud.eval_js("""
    const items = document.querySelectorAll('.item');
    Array.from(items).map(el => el.textContent);
""")

# With custom timeout
result = stx.cloud.eval_js("longRunningFunction()", timeout=30)
```

---

## ui_action

Drives browser UI actions programmatically: navigation, highlight, click, fill, scroll, etc.

```python
ui_action(steps: list, delay_ms: int = 900, **kw) -> dict
```

**Parameters**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `steps` | `list` | required | List of action step dicts. Each dict describes one browser action. |
| `delay_ms` | `int` | `900` | Milliseconds to wait between steps. |
| `**kw` | any | — | Forwarded to `CloudClient.__init__`. |

**Returns:** `dict` — result summary from `scitex_cloud`.

**Implementation:** `_Client(**kw).ui_action(steps, delay_ms)`

### Step Format

Each step is a dict. The exact keys are defined by `scitex_cloud`. Common action types include `navigate`, `click`, `fill`, `scroll`, and `highlight`.

### Examples

```python
import scitex as stx

# Single click
stx.cloud.ui_action([
    {"action": "click", "selector": "#submit-btn"}
])

# Multi-step: navigate then fill a form
stx.cloud.ui_action([
    {"action": "navigate", "url": "/dashboard"},
    {"action": "fill", "selector": "#search-input", "value": "my query"},
    {"action": "click", "selector": "#search-btn"},
], delay_ms=500)

# With custom delay between steps
stx.cloud.ui_action(
    steps=[
        {"action": "scroll", "selector": "#results", "direction": "down"},
    ],
    delay_ms=200,
)
```

---

## Notes

- Both functions require an active browser connection managed by `scitex-cloud`.
- `**kw` passes authentication or connection options to `CloudClient` — see `scitex-cloud` docs for supported kwargs.
- Raises `ImportError` if `scitex-cloud` is not installed (see [availability.md](availability.md)).
