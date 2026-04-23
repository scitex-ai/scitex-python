---
name: interface-python-api
description: Python API design rules for SciTeX packages — minimal exposure, scitex-io examples, introspect commands.
---

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

## Import conventions — standalone vs umbrella

Every SciTeX subpackage ships in two ways. **Both must be documented in
every package's skill / README** because which one a user has installed
is outside the skill's control.

| Install command             | Required import                      | Notes |
|-----------------------------|--------------------------------------|-------|
| `pip install scitex-io`     | `import scitex_io as sio`            | Standalone top-level module; no `scitex.` namespace available |
| `pip install scitex` (umbrella) | `import scitex.io as sio`        | `scitex` re-exports the standalone package under `scitex.io` via lazy-module machinery |
| `pip install scitex scitex-io` | either works                      | Both imports resolve to the same module object |

Empirically verified 2026-04-23 in a fresh `python:3.11` container:

```text
pip install scitex-io        → import scitex_io as sio  ✓
                             → import scitex.io as sio  ✗  (ModuleNotFoundError: 'scitex')
```

### Rule for documentation

- **Skill / README examples MUST show both forms** side-by-side, with a
  one-line note on when each applies. Readers land on the skill without
  knowing which install path they took.
- **Inside the package's own source code**: use the standalone form
  (`from scitex_io import save`) — the package cannot assume the
  umbrella is installed alongside it.
- **In ecosystem docs that assume the umbrella**: use
  `import scitex` (not `import scitex as stx`) in all examples.
  Aliases belong to the user, not the documentation.

### Example — side-by-side (copy into package skills)

```python
# If you installed the standalone:
#     pip install scitex-io
import scitex_io as sio
sio.save(df, "results.csv")

# If you installed the umbrella:
#     pip install scitex
import scitex.io as sio
sio.save(df, "results.csv")
```

Both forms call the same function; the difference is which module
namespace Python resolves. Choose the install path that matches the
project's dependency story — standalone if the package is a leaf
dependency, umbrella if the project uses many SciTeX packages at once.
