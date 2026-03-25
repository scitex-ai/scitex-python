---
description: Access project files through a unified storage interface with get_files(), register custom backends with register_backend(), and type-check with the FilesBackend protocol.
---

# File Access

## get_files

Return a `FilesBackend` instance for a given project path. The backend is auto-detected from the path (local directory, S3 URI, etc.).

```python
get_files(project_path: str) -> FilesBackend
```

```python
import scitex as stx

# Local directory backend
files = stx.app.get_files("./my_project")
content = files.read("results/output.csv")
files.write("results/summary.txt", "Accuracy: 0.93\n")

# Cloud backend (if S3 backend registered)
files = stx.app.get_files("s3://my-bucket/project")
```

---

## register_backend

Register a custom storage backend factory.

```python
register_backend(scheme: str, factory: Callable[[str], FilesBackend]) -> None
```

```python
import scitex as stx

class MyS3Backend:
    def __init__(self, path): ...
    def read(self, key): ...
    def write(self, key, data): ...

stx.app.register_backend("s3", lambda path: MyS3Backend(path))

# Now get_files("s3://...") will use MyS3Backend
files = stx.app.get_files("s3://my-bucket/project")
```

---

## FilesBackend

Protocol type defining the required interface for any backend.

```python
class FilesBackend(Protocol):
    def read(self, key: str) -> bytes: ...
    def write(self, key: str, data: bytes | str) -> None: ...
```

Use for type annotations:

```python
import scitex as stx

def process(files: stx.app.FilesBackend) -> None:
    data = files.read("data.npy")
```
