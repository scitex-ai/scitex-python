---
name: stx.datetime
description: Datetime utilities for linearly spaced arrays, timestamp normalization, and format conversion.
---

# stx.datetime

The `stx.datetime` module provides utilities for datetime operations commonly needed in scientific data analysis. Also accessible as `stx.dt` (exact alias).

## Sub-skills

- [linspace.md](linspace.md) — `linspace()` for evenly spaced datetime arrays by count or sampling rate
- [timestamp-normalization.md](timestamp-normalization.md) — `normalize_timestamp`, `to_datetime`, `format_for_filename`, `format_for_display`, `get_time_delta_seconds`, `validate_timestamp_format`

## Quick Reference

```python
import scitex as stx
import datetime

# Evenly spaced datetime array
start = datetime.datetime(2024, 1, 1)
end   = datetime.datetime(2024, 1, 2)
times = stx.datetime.linspace(start, end, sampling_rate=1000.0)  # 1 kHz

# Parse any timestamp format
dt = stx.datetime.to_datetime("2024-01-15T10:30:00")
dt = stx.datetime.to_datetime(1705312200)  # Unix timestamp

# Normalize to STANDARD_FORMAT = "%Y-%m-%d %H:%M:%S"
s = stx.datetime.normalize_timestamp(dt, return_as="str", normalize_utc=False)

# Filename-safe format
fname = stx.datetime.format_for_filename(dt)  # "20240115_103000"

# Time difference
delta = stx.datetime.get_time_delta_seconds(start, end)  # seconds

# Same API via stx.dt (alias)
stx.dt.linspace(start, end, n_samples=100)
```

## Constants

| Constant | Value |
|----------|-------|
| `STANDARD_FORMAT` | `"%Y-%m-%d %H:%M:%S"` (configurable via CONFIG) |
| `ALTERNATIVE_FORMATS` | 16 common timestamp formats tried when parsing |
