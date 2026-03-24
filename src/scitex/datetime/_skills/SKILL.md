---
name: stx.datetime
description: Datetime utilities for linearly spaced arrays, timestamp normalization, and format conversion.
---

# stx.datetime

The `stx.datetime` module provides utilities for datetime operations commonly needed in scientific data analysis: creating linearly spaced datetime sequences, normalizing timestamps to a consistent format, and converting between various datetime representations.

## Python API

```python
import scitex as stx

# Create linearly spaced datetime array
times = stx.datetime.linspace(start="2024-01-01", end="2024-12-31", n=365)

# Normalize timestamps to standard format
normalized = stx.datetime.normalize_timestamp("2024-01-15T10:30:00")

# Convert various formats to datetime
dt = stx.datetime.to_datetime("20240115_103000")
dt = stx.datetime.to_datetime(1705312200)  # Unix timestamp

# Format for filenames (no colons/spaces)
fname_ts = stx.datetime.format_for_filename(dt)  # "20240115_103000"

# Format for display
disp_ts = stx.datetime.format_for_display(dt)  # "2024-01-15 10:30:00"

# Calculate time delta
delta_sec = stx.datetime.get_time_delta_seconds("10:00:00", "10:05:30")  # 330.0

# Validate format
is_valid = stx.datetime.validate_timestamp_format("2024-01-15 10:30:00")

# Constants
print(stx.datetime.STANDARD_FORMAT)  # "%Y-%m-%d %H:%M:%S"
```

## Key Features

- `linspace(start, end, n)` — create N evenly-spaced datetime points
- `normalize_timestamp` — standardize timestamps to `STANDARD_FORMAT`
- `to_datetime` — convert strings, Unix timestamps, and other formats to datetime
- `format_for_filename` / `format_for_display` — format datetimes for different contexts
- `get_time_delta_seconds` — compute difference between two timestamps in seconds
- Also accessible as `stx.dt` (alias module)
