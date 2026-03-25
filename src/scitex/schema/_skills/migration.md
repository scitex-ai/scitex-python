---
name: schema-migration
description: Migrate from deprecated scitex.schema imports to scitex.io.bundle.
---

# Schema Migration

## Before (deprecated)

```python
from scitex.schema import FTS, Node, Encoding, Theme, Stats
from scitex.schema import validate_figure, ValidationError
```

## After (preferred)

```python
from scitex.io.bundle import FTS, Node, Encoding, Theme, Stats
```

Validation functions are only temporarily available in `scitex.schema` during the migration period. Check `scitex.io.bundle` for the canonical location.
