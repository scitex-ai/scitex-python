---
name: stx.schema
description: DEPRECATED — schema definitions migrating to stx.io.bundle. Emits DeprecationWarning on import.
---

# stx.schema — Skills Index

Deprecated module. Core bundle schemas (FTS, Node, Encoding, Theme, Stats) have moved to `scitex.io.bundle`. Plot, encoding, theme, figure, stats, and validation schemas are temporarily still here.

## Sub-skills

| File | Description |
|------|-------------|
| [deprecated-alias.md](deprecated-alias.md) | Migration guide; list of schemas in scitex.io.bundle vs still in scitex.schema |

## Quick Reference

```python
# Bundle schemas → migrate now
from scitex.io.bundle import FTS, Node, Encoding, Theme, Stats, BBox, SizeMM, DataInfo

# Plot/encoding/theme schemas → still in scitex.schema (for now)
from scitex.schema import PlotSpec, PlotStyle, PlotEncoding, validate_figure
```
