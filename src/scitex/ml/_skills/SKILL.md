---
name: stx.ml
description: Backward-compatibility alias for stx.ai — machine learning utilities.
---

# stx.ml — Skills Index

`stx.ml` is a backward-compatibility re-export of `scitex.ai`. All ML functionality lives in `scitex.ai`; this module exists only so old imports continue working.

## Sub-skills

| File | Description |
|------|-------------|
| [alias-for-ai.md](alias-for-ai.md) | Migration guide and list of available submodules |

## Quick Reference

```python
# Old (still works)
import scitex as stx
stx.ml.classification   # same as stx.ai.classification

# New (preferred)
from scitex.ai import classification
```

## Note

New code should import from `scitex.ai` directly. `stx.ml` will not be removed but may not receive new features.
