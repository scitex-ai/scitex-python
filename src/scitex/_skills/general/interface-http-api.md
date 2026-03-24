---
name: interface-http-api
description: Optional HTTP API via FastAPI — delegation rules, when to use.
---

# HTTP API (Optional)

Use FastAPI when a package needs web-accessible endpoints. Not required for most packages.

## When to Use

- Package serves web clients (e.g., scitex-cloud)
- Need REST endpoints for external integrations
- Dashboard or web UI requires backend API

## Rules

- No original logic — always delegate to Python API
- Use FastAPI (not Flask, Django REST)
- JSON responses, standard HTTP status codes
- OpenAPI docs auto-generated at `/docs`

## Example

```python
from fastapi import FastAPI
from scitex_io import save, load, list_formats

app = FastAPI(title="scitex-io API")

@app.get("/formats")
def get_formats():
    return list_formats()

@app.post("/load")
def load_file(path: str):
    data = load(path)
    return {"data": str(data)}
```

## Packages Using HTTP API

- `scitex-cloud` — Django + FastAPI for cloud infrastructure
- Most packages do NOT need this interface
