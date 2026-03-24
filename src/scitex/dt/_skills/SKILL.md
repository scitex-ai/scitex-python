---
name: stx.dt
description: Short alias for stx.datetime — datetime utilities for timestamps, normalization, and formatting.
---

# stx.dt

The `stx.dt` module is a short alias for `stx.datetime`, providing the same datetime utilities under a more concise name. Both modules are fully supported and interchangeable.

## Python API

```python
import scitex as stx

# Create linearly spaced datetime array
times = stx.dt.linspace(start="2024-01-01", end="2024-12-31", n=365)

# Normalize timestamps
normalized = stx.dt.normalize_timestamp("2024-01-15T10:30:00")

# Convert to datetime object
dt = stx.dt.to_datetime("20240115_103000")

# Format for filenames
fname = stx.dt.format_for_filename(dt)  # "20240115_103000"

# Format for display
display = stx.dt.format_for_display(dt)  # "2024-01-15 10:30:00"

# Time delta
delta = stx.dt.get_time_delta_seconds("10:00:00", "10:05:30")

# Validate format
is_valid = stx.dt.validate_timestamp_format("2024-01-15 10:30:00")
```

## Key Features

- Full alias for `stx.datetime` — all the same functions available
- `linspace` — linearly spaced datetime arrays
- `normalize_timestamp` / `to_datetime` — timestamp parsing and normalization
- `format_for_filename` / `format_for_display` — context-appropriate formatting
- `STANDARD_FORMAT` / `ALTERNATIVE_FORMATS` — format string constants
