# Timestamp Normalization with stx.datetime

The timestamp normalization utilities standardize diverse timestamp representations to a single consistent format.

## STANDARD_FORMAT

The standard format is `"%Y-%m-%d %H:%M:%S"` (configurable via `CONFIG.FORMATS.TIMESTAMP` in project configs).

```python
from scitex.datetime import STANDARD_FORMAT, ALTERNATIVE_FORMATS

print(STANDARD_FORMAT)        # "%Y-%m-%d %H:%M:%S"
print(ALTERNATIVE_FORMATS[0]) # "%Y-%m-%dT%H:%M:%S.%f"
```

`ALTERNATIVE_FORMATS` contains 16 common formats tried in order when parsing strings.

## normalize_timestamp

Convert any timestamp to a standard string, datetime object, or Unix float:

```python
from scitex.datetime import normalize_timestamp
from datetime import datetime

dt = datetime(2010, 6, 18, 10, 15, 0)

# String output (default, no UTC conversion)
normalize_timestamp(dt, return_as="str", normalize_utc=False)
# -> "2010-06-18 10:15:00"

# datetime output
normalize_timestamp(dt, return_as="datetime", normalize_utc=False)
# -> datetime(2010, 6, 18, 10, 15, 0)

# Unix timestamp float
normalize_timestamp(dt, return_as="timestamp", normalize_utc=False)
# -> 1276856100.0

# Parse from string
normalize_timestamp("2010-06-18T10:15:00", return_as="str", normalize_utc=False)
# -> "2010-06-18 10:15:00"

# Parse from Unix timestamp
normalize_timestamp(1276856100, return_as="str", normalize_utc=False)
# -> "2010-06-18 10:15:00"
```

## to_datetime

Convert any supported format directly to a `datetime` object:

```python
from scitex.datetime import to_datetime

# From datetime (passthrough)
to_datetime(datetime(2010, 6, 18, 10, 15, 0))

# From ISO 8601 string
to_datetime("2010-06-18T10:15:00")

# From various string formats
to_datetime("18/06/2010 10:15:00")

# From Unix timestamp (int or float)
to_datetime(1276856100)
to_datetime(1276856100.5)
```

Nanosecond precision is handled by truncating to microseconds automatically.

## Format Utilities

```python
from scitex.datetime import format_for_filename, format_for_display
from datetime import datetime

dt = datetime(2010, 6, 18, 10, 15, 0)

format_for_filename(dt)   # "20100618_101500" (safe for file names)
format_for_display(dt)    # "2010-06-18 10:15:00" (human readable)
```

## validate_timestamp_format

```python
from scitex.datetime import validate_timestamp_format

validate_timestamp_format("2024-01-15 10:30:00")  # True
validate_timestamp_format("2024-01-15T10:30:00")  # False (non-standard)
validate_timestamp_format("not a date")            # False
```

## get_time_delta_seconds

```python
from scitex.datetime import get_time_delta_seconds

delta = get_time_delta_seconds("2024-01-01 00:00:00", "2024-01-01 01:30:45")
# -> 5445.0 (float seconds)

# Also works with datetime objects
delta = get_time_delta_seconds(start_dt, end_dt)
```

## parse_patient_recording_start_format

Specialized parser for clinical recording timestamps in `"DD/MM/YYYY, HH:MM:SS"` format:

```python
from scitex.datetime import parse_patient_recording_start_format

dt = parse_patient_recording_start_format("10/06/2010, 07:40:34")
# -> datetime(2010, 6, 10, 7, 40, 34)
```
