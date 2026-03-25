---
name: stx.verify — Deprecated Alias for stx.clew
description: scitex.verify is a deprecated backward-compat shim. All verification functionality lives in scitex.clew.
---

# stx.verify — Deprecated Alias

`scitex.verify` re-exports everything from `scitex.clew` via `from scitex.clew import *`. It emits `DeprecationWarning` on import.

## Migration

```python
# Old (triggers DeprecationWarning on import)
from scitex.verify import status, run, chain, dag

# New (preferred)
from scitex.clew import status, run, chain, dag
import scitex as stx
stx.clew.status()
stx.clew.run(session_id)
stx.clew.chain("results/output.csv")
stx.clew.dag(["file1.csv", "file2.png"])
```

See the `stx.clew` skills for full documentation on hash-based verification, chain of custody, and DAG tracing.
