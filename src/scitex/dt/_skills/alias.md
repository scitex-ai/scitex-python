---
name: dt-alias
description: stx.dt is a shorter alias for stx.datetime. All exported names are identical.
---

# stx.dt Alias

`stx.dt` and `stx.datetime` export exactly the same names:

| `stx.dt.*` | `stx.datetime.*` |
|-----------|-----------------|
| `linspace` | `linspace` |
| `normalize_timestamp` | `normalize_timestamp` |
| `to_datetime` | `to_datetime` |
| `format_for_filename` | `format_for_filename` |
| `format_for_display` | `format_for_display` |
| `validate_timestamp_format` | `validate_timestamp_format` |
| `get_time_delta_seconds` | `get_time_delta_seconds` |
| `parse_patient_recording_start_format` | `parse_patient_recording_start_format` |
| `STANDARD_FORMAT` | `STANDARD_FORMAT` |
| `ALTERNATIVE_FORMATS` | `ALTERNATIVE_FORMATS` |

```python
import scitex as stx

# These are equivalent
stx.dt.linspace("2026-01-01", "2026-12-31", n=12)
stx.datetime.linspace("2026-01-01", "2026-12-31", n=12)
```

For full documentation see the `datetime` skill.
