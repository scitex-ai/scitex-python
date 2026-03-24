---
name: stx.app
description: Unified file storage SDK for local and cloud application backends.
---

# stx.app

The `stx.app` module provides a unified file storage SDK that abstracts over local and cloud backends. It auto-detects the appropriate backend (local filesystem, S3, etc.) and provides a consistent interface for file access.

## Python API

```python
import scitex as stx

# Auto-detect backend and get files
files = stx.app.get_files("./project")

# Register a custom storage backend
stx.app.register_backend("s3", my_s3_factory)

# Type annotation for backend protocols
backend: stx.app.FilesBackend = stx.app.get_files("./data")
```

## Key Features

- `get_files(path)` — auto-detect backend (local or cloud) and return file accessor
- `register_backend(name, factory)` — register a custom storage backend
- `FilesBackend` — protocol type for type annotations
- Thin re-export layer over the standalone `scitex-app` package
