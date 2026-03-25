---
description: Check scitex-cloud service health and retrieve version with health_check() and get_version().
---

# Health Check and Version

## get_version

Returns the version string of the installed `scitex-cloud` package.

```python
get_version() -> str
```

**Parameters:** none

**Returns:** version string, e.g. `"0.7.0a0"`

**Source:** Re-exported directly from `scitex_cloud.get_version`.

```python
import scitex as stx

version = stx.cloud.get_version()
print(version)  # "0.7.0a0"
```

---

## health_check

Verifies the cloud service is running and reachable.

```python
health_check() -> dict
```

**Parameters:** none

**Returns:** dict with at minimum a `"status"` key.

```python
import scitex as stx

status = stx.cloud.health_check()
# {"status": "healthy", ...}
```

**Source:** Re-exported directly from `scitex_cloud.health_check`.

---

## Pattern: Guard with AVAILABLE

```python
import scitex as stx

if not stx.cloud.AVAILABLE:
    raise RuntimeError("scitex-cloud required but not installed")

status = stx.cloud.health_check()
assert status["status"] == "healthy", f"Cloud unhealthy: {status}"

version = stx.cloud.get_version()
print(f"Connected to scitex-cloud {version}")
```
