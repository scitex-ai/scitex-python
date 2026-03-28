---
name: stx.rng
description: DEPRECATED — random state utilities merged into stx.repro. Use stx.repro for all new code.
---

# stx.rng — Skills Index

Deprecated module. Random state management has moved to `scitex.repro`.

## Sub-skills

| File | Description |
|------|-------------|
| [deprecated-alias.md](deprecated-alias.md) | Migration guide from scitex.rng to scitex.repro |

## Quick Reference

```python
# Old (triggers DeprecationWarning on import)
from scitex.rng import RandomStateManager

# New (preferred)
from scitex.repro import RandomStateManager, get, reset
```
