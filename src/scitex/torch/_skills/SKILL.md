---
name: stx.torch
description: PyTorch utilities for NaN-safe tensor operations and applying arbitrary functions across tensor dimensions.
user-invocable: false
---

# stx.torch — PyTorch Utilities

Utility functions that fill gaps in the PyTorch standard library. Accessed
via `import scitex as stx` then `stx.torch.<function>`.

## Sub-skills

### NaN-Safe Aggregations
- [nan-funcs.md](nan-funcs.md) — `nanmax`, `nanmin`, `nanstd`, `nanvar`, `nanprod`, `nancumsum`, `nancumprod`, `nanargmax`, `nanargmin`: NaN-tolerant versions of common reduction and cumulative operations that PyTorch does not provide natively

### Dimension-Wise Function Application
- [apply-to.md](apply-to.md) — `apply_to(fn, x, dim)`: apply any callable along a specified tensor dimension via permute + unbind + stack
