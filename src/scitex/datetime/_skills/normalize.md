---
description: Normalize diverse timestamp formats to a standard string with normalize_timestamp(), convert to datetime with to_datetime(), format for filenames or display, calculate time deltas, and validate format strings.
---

# Timestamp Normalization

## STANDARD_FORMAT

The canonical timestamp format string: `"%Y-%m-%d %H:%M:%S"`.

```python
import scitex as stx

print(stx.datetime.STANDARD_FORMAT)
# '%Y-%m-%d %H:%M:%S'
```

---

## normalize_timestamp

Convert any timestamp representation to the standard format string.

```python
normalize_timestamp(ts) -> str
```

Accepts: `str`, `datetime`, `float` (Unix epoch), `np.datetime64`, `pd.Timestamp`.

```python
import scitex as stx

stx.datetime.normalize_timestamp(1700000000.0)      # '2023-11-14 22:13:20'
stx.datetime.normalize_timestamp("2026/01/15")      # '2026-01-15 00:00:00'
```

---

## to_datetime

Convert any timestamp representation to a `datetime.datetime` object.

```python
to_datetime(ts) -> datetime
```

```python
import scitex as stx

dt = stx.datetime.to_datetime("2026-01-15 08:30:00")
print(dt.year, dt.hour)  # 2026  8
```

---

## format_for_filename

Format a timestamp as a safe filename component (no colons or spaces).

```python
format_for_filename(ts) -> str
```

```python
import scitex as stx

s = stx.datetime.format_for_filename("2026-01-15 08:30:00")
print(s)  # '2026-01-15_08-30-00'
```

---

## format_for_display

Format a timestamp for human-readable display.

```python
format_for_display(ts) -> str
```

---

## validate_timestamp_format

Return `True` if a string matches the standard format.

```python
validate_timestamp_format(s: str) -> bool
```

---

## get_time_delta_seconds

Calculate the number of seconds between two timestamps.

```python
get_time_delta_seconds(start, end) -> float
```

```python
import scitex as stx

delta = stx.datetime.get_time_delta_seconds(
    "2026-01-01 00:00:00",
    "2026-01-01 01:30:00",
)
print(delta)  # 5400.0
```
