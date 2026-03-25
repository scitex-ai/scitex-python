---
name: rng-migration
description: Migrate from deprecated scitex.rng to scitex.repro. RandomStateManager, get, and reset are now in stx.repro.
---

# rng Migration

`scitex.rng` is deprecated. All three exports (`RandomStateManager`, `get`, `reset`) live in `scitex.repro`.

## Before (deprecated)

```python
from scitex.rng import RandomStateManager
rng = RandomStateManager(seed=42)
```

## After (preferred)

```python
from scitex.repro import RandomStateManager
rng = RandomStateManager(seed=42)
```

Or via the top-level alias:

```python
import scitex as stx

rng = stx.repro.RandomStateManager(seed=42)
data = rng("data").random(100)
```

See the `repro` skill for full documentation.
