---
name: container-inspect
description: Query container runtime status, detect the container command (apptainer/singularity), and find the containers directory.
---

# Container Inspection

## status

Return a status dict for the current container environment.

```python
status() -> dict
```

```python
import scitex as stx

info = stx.container.status()
print(info)
# {'active_version': 'v1.1', 'containers_dir': '/scratch/containers/proj', ...}
```

---

## detect_container_cmd

Discover which container runtime is available on the system.

```python
detect_container_cmd() -> str | None
```

Returns `"apptainer"`, `"singularity"`, or `None`.

```python
import scitex as stx

cmd = stx.container.detect_container_cmd()
print(cmd)  # 'apptainer'
```

---

## find_containers_dir

Locate the project containers directory based on config or environment variables.

```python
find_containers_dir() -> str | None
```

```python
import scitex as stx

cdir = stx.container.find_containers_dir()
print(cdir)  # '/scratch/containers/myproject'
```
