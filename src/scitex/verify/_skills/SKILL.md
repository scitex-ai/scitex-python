---
name: stx.verify
description: DEPRECATED — backward-compat alias for stx.clew. Use stx.clew for all new code.
---

# stx.verify — Skills Index

Deprecated module. All verification functionality has moved to `scitex.clew`.

## Sub-skills

| File | Description |
|------|-------------|
| [deprecated-alias.md](deprecated-alias.md) | Migration guide from scitex.verify to scitex.clew |

## Quick Reference

```python
# Old (triggers DeprecationWarning on import)
from scitex.verify import status, run, chain

# New (preferred)
from scitex.clew import status, run, chain
```
