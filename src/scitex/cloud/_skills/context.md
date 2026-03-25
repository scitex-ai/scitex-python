---
name: cloud-context
description: Retrieve the current web app context (username, page state, available actions) with get_context().
---

# Web App Context

## get_context

Returns the current state of the user's active web app session: who is logged in, what page is open, what skills and actions are available.

```python
get_context(page: str = "", **kw) -> dict
```

**Parameters**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `page` | `str` | `""` | Page name or URL fragment to query context for. Pass `""` for the current page. |
| `**kw` | any | — | Forwarded to `CloudClient.__init__` (e.g., auth credentials, base URL). |

**Returns:** `dict` — keys include at minimum `"username"`, `"page"`, and `"actions"`. Exact shape is defined by `scitex_cloud`.

**Implementation:** `_Client(**kw).get_context(page)` where `_Client` is `scitex_cloud.api.CloudClient`.

---

## Examples

```python
import scitex as stx

# Current page context
ctx = stx.cloud.get_context()
print(ctx["username"])  # logged-in user
print(ctx["actions"])   # list of available actions on current page

# Context for a specific page
ctx = stx.cloud.get_context("dashboard")
print(ctx["page"])
```

---

## Notes

- Requires the browser/client to be connected to scitex-cloud.
- The `**kw` forwarded to `CloudClient` allows passing custom host, port, auth tokens, etc. — see `scitex-cloud` documentation for supported kwargs.
- Raises `ImportError` if `scitex-cloud` is not installed (see [availability.md](availability.md)).
