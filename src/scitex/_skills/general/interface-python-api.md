---
name: interface-python-api
description: Python API design rules for SciTeX packages — minimal exposure, scitex-io examples, introspect commands.
---

> General patterns: see [programming-common/interface-python-api.md](../../commands/.claude/skills/programming-common/interface-python-api.md)

# Python API (SciTeX)

## scitex-io Example

```python
# src/scitex_io/__init__.py
from ._save import save
from ._load import load
from ._load_configs import load_configs
from ._registry import register_saver, register_loader, list_formats
from ._metadata import embed_metadata, read_metadata, has_metadata
from ._glob import glob, parse_glob
from ._utils import DotDict

__all__ = [
    "save", "load", "load_configs",
    "register_saver", "register_loader", "list_formats",
    "embed_metadata", "read_metadata", "has_metadata",
    "glob", "parse_glob", "DotDict",
]
```

## API Introspection (SciTeX Commands)

```bash
# Package-level
scitex-io list-python-apis        # Names only
scitex-io list-python-apis -v     # + signatures
scitex-io list-python-apis -vv    # + docstrings

# Module-level (via scitex umbrella)
scitex audio list-python-apis
scitex introspect api scitex.audio

# Both should show consistent, minimal public API
```

## SciTeX-Specific Rule

- Use `import scitex` (not `import scitex as stx`) in all documentation examples
