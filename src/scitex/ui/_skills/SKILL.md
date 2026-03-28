---
name: stx.ui
description: DEPRECATED notification shim — use stx.notify for all new code.
---

# stx.ui — Skills Index

Deprecated module. All notification functionality has moved to `scitex.notify`.

## Sub-skills

| File | Description |
|------|-------------|
| [deprecated-alias.md](deprecated-alias.md) | Migration guide from scitex.ui to scitex.notify; wrapper table |

## Quick Reference

```python
# Old (triggers DeprecationWarning on each call)
import scitex as stx
stx.ui.alert("Done")

# New (preferred)
stx.notify.alert("Done")
```
