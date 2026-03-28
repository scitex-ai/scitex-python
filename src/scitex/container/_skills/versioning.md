---
description: List, switch, rollback, and clean up container versions to maintain reproducible HPC execution environments.
---

# Container Versioning

## list_versions

List all deployed container versions.

```python
list_versions(containers_dir: str | None = None) -> list[str]
```

```python
import scitex as stx

versions = stx.container.list_versions()
print(versions)  # ['v1.0', 'v1.1', 'v2.0-dev']
```

---

## get_active_version

Return the currently active (symlinked) version.

```python
get_active_version(containers_dir: str | None = None) -> str | None
```

```python
import scitex as stx

active = stx.container.get_active_version()
print(active)  # 'v1.1'
```

---

## switch_version

Switch the active version by updating the symlink.

```python
switch_version(version: str, containers_dir: str | None = None) -> dict
```

```python
import scitex as stx

stx.container.switch_version("v2.0-dev")
```

---

## rollback

Switch back to the previous version.

```python
rollback(containers_dir: str | None = None) -> dict
```

---

## cleanup

Remove old container versions that are no longer active.

```python
cleanup(containers_dir: str | None = None, keep: int = 2) -> dict
```

```python
import scitex as stx

# Keep the 2 most recent versions; delete the rest
stx.container.cleanup(keep=2)
```
