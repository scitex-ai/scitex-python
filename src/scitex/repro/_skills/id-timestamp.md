---
description: Generate unique experiment IDs with gen_ID(), create ISO-format timestamps with gen_timestamp(), and use their short aliases gen_id() and timestamp().
---

# ID and Timestamp

## gen_ID / gen_id

Generate a short unique identifier (UUID-like) for labeling experiment runs.

```python
gen_ID() -> str
gen_id() -> str   # alias
```

```python
import scitex as stx

run_id = stx.repro.gen_ID()
print(run_id)  # e.g., 'a3f2b1c9'

# Use as output directory suffix
import os
os.makedirs(f"results_{run_id}", exist_ok=True)
```

---

## gen_timestamp / timestamp

Return the current time as a formatted string.

```python
gen_timestamp() -> str
timestamp() -> str   # alias
```

Returns a string in the format `"YYYYMMDD_HHMMSS"` (safe for filenames).

```python
import scitex as stx

ts = stx.repro.gen_timestamp()
print(ts)  # e.g., '20260325_143022'

# Tag outputs with timestamp
stx.io.save(fig, f"plot_{ts}.png")
```
