---
name: stx.reproduce
description: DEPRECATED — backward-compat alias for stx.repro. Use stx.repro for all new code.
---

# stx.reproduce — Skills Index

Deprecated module. All functionality has moved to `scitex.repro`.

## Sub-skills

| File | Description |
|------|-------------|
| [deprecated-alias.md](deprecated-alias.md) | Migration guide from scitex.reproduce to scitex.repro |

## Quick Reference

```python
# Old (triggers DeprecationWarning on import)
from scitex.reproduce import RandomStateManager

# New (preferred)
from scitex.repro import RandomStateManager
```
