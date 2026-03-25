# stx.dt — Short Alias for stx.datetime

`stx.dt` is an exact alias for `stx.datetime`. All functions, constants, and behaviors are identical. The shorter name is provided for convenience in interactive sessions.

## Available Functions

All functions from `stx.datetime` are available under `stx.dt`:

```python
import scitex as stx
import datetime

# Linearly spaced datetime array
start = datetime.datetime(2024, 1, 1)
end   = datetime.datetime(2024, 1, 2)

times = stx.dt.linspace(start, end, n_samples=1000)
times = stx.dt.linspace(start, end, sampling_rate=1000.0)

# Parse any timestamp format to datetime
dt = stx.dt.to_datetime("2024-01-15T10:30:00")
dt = stx.dt.to_datetime(1705312200)  # Unix timestamp

# Normalize to STANDARD_FORMAT
s = stx.dt.normalize_timestamp(dt, return_as="str", normalize_utc=False)
# "2024-01-15 10:30:00"

# Format for filenames (no spaces or colons)
fname = stx.dt.format_for_filename(dt)  # "20240115_103000"

# Format for display
display = stx.dt.format_for_display(dt)  # "2024-01-15 10:30:00"

# Compute time difference
delta = stx.dt.get_time_delta_seconds(start, end)  # 86400.0

# Validate format
stx.dt.validate_timestamp_format("2024-01-15 10:30:00")  # True

# Clinical recording format parser
dt = stx.dt.parse_patient_recording_start_format("10/06/2010, 07:40:34")
```

## Constants

```python
stx.dt.STANDARD_FORMAT    # "%Y-%m-%d %H:%M:%S"
stx.dt.ALTERNATIVE_FORMATS  # list of 16 formats tried when parsing
```

## Choosing Between stx.dt and stx.datetime

Both are fully interchangeable. Use `stx.dt` for brevity in scripts and notebooks. Use `stx.datetime` when code clarity is more important than conciseness (e.g., in library code that will be read by others).

```python
# These are equivalent
stx.dt.to_datetime("2024-01-15")
stx.datetime.to_datetime("2024-01-15")
```

For detailed documentation of each function, see the sub-skills in `stx.datetime/_skills/`.
