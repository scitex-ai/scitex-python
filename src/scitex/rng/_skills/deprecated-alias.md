---
description: scitex.rng is a deprecated backward-compat shim. All functionality lives in scitex.repro.
---

# stx.rng — Deprecated Alias

`scitex.rng` re-exports `RandomStateManager`, `get`, and `reset` from `scitex.repro`. It emits a `DeprecationWarning` on import.

## Migration

```python
# Old (triggers DeprecationWarning)
from scitex.rng import RandomStateManager, get, reset

# New (preferred)
from scitex.repro import RandomStateManager, get, reset
```

See [stx.repro random-state-manager.md](../../repro/_skills/random-state-manager.md) for full documentation.
