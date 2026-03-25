---
description: scitex.verify is deprecated. Migrate all imports to scitex.clew.
---

# verify Migration

`scitex.verify` is a deprecated alias for `scitex.clew`. Replace all imports:

## Before (deprecated)

```python
import scitex.verify as verify
from scitex.verify import run, chain
```

## After (preferred)

```python
import scitex.clew as clew
from scitex.clew import run, chain
```

Or via top-level alias:

```python
import scitex as stx

stx.clew.run("my_experiment")
```

See the `clew` skill for full documentation of the verification system.
