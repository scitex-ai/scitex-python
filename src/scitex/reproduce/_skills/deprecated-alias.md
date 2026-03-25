---
name: stx.reproduce — Deprecated Alias for stx.repro
description: scitex.reproduce is a deprecated backward-compat shim. All functionality lives in scitex.repro.
---

# stx.reproduce — Deprecated Alias

`scitex.reproduce` is a thin shim that re-exports everything from `scitex.repro`. It emits a `DeprecationWarning` on import.

## Migration

```python
# Old (triggers DeprecationWarning)
from scitex.reproduce import RandomStateManager, gen_id, gen_timestamp, hash_array

# New (preferred)
from scitex.repro import RandomStateManager, gen_id, gen_timestamp, hash_array
```

See the `stx.repro` skills for full documentation:
- [random-state-manager.md](../../repro/_skills/random-state-manager.md)
- [id-timestamp-hash.md](../../repro/_skills/id-timestamp-hash.md)
