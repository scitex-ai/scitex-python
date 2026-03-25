---
name: stx.dt
description: Short alias for stx.datetime — all the same datetime utilities under a more concise name.
---

# stx.dt

`stx.dt` is an exact alias for `stx.datetime`. Both modules export the same functions and constants. The shorter name is for convenience.

## Sub-skills

- [dt-alias.md](dt-alias.md) — Complete function reference with examples, choosing between `stx.dt` and `stx.datetime`

## Quick Reference

```python
import scitex as stx
import datetime

# Linearly spaced datetimes
start = datetime.datetime(2024, 1, 1)
end   = datetime.datetime(2024, 1, 2)
times = stx.dt.linspace(start, end, sampling_rate=1000.0)

# Parse any timestamp
dt = stx.dt.to_datetime("2024-01-15T10:30:00")
s  = stx.dt.normalize_timestamp(dt, return_as="str")

# Format for filenames
fname = stx.dt.format_for_filename(dt)  # "20240115_103000"

# Time delta
delta = stx.dt.get_time_delta_seconds(start, end)

# Validate
stx.dt.validate_timestamp_format("2024-01-15 10:30:00")  # True
```

For detailed function documentation see `stx.datetime/_skills/`:
- linspace: `stx.datetime/_skills/linspace.md`
- Timestamp normalization: `stx.datetime/_skills/timestamp-normalization.md`
