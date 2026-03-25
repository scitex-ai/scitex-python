---
name: stx.repro — ID, Timestamp, and Hash Utilities
description: Generate unique experiment IDs with timestamps, filename-safe timestamp strings, and SHA256 hashes of arrays.
---

# stx.repro — ID, Timestamp, and Hash Utilities

## gen_id — unique experiment IDs

Combines a formatted timestamp with random alphanumeric characters.

```python
from scitex.repro import gen_id

eid = gen_id()
# "2025Y-05M-31D-12h30m45s_a3Bc9xY2"  (default format, 8 random chars)

eid = gen_id(time_format="%Y%m%d", N=4)
# "20250531_xY9a"

# Use in file paths
save_path = f"results/experiment_{gen_id()}.pkl"
```

Parameters:
- `time_format` — `strftime` format string; default `"%YY-%mM-%dD-%Hh%Mm%Ss"`
- `N` — number of random alphanumeric chars to append; default 8

`gen_ID` is a backward-compat alias for `gen_id`.

## gen_timestamp — filename-safe timestamp

Returns a compact timestamp string suitable for filenames.

```python
from scitex.repro import gen_timestamp, timestamp

ts = gen_timestamp()
# "2025-0531-1230"   (format: YYYY-MMDD-HHMM)

fname = f"report_{gen_timestamp()}.csv"

ts = timestamp()    # alias for gen_timestamp
```

Format is `"%Y-%m%d-%H%M"`. Minute-level precision; no seconds or special chars.

## hash_array — change detection

Compute a deterministic 32-hex-char SHA256 hash of a numeric array to detect data drift or verify inputs.

```python
from scitex.repro import hash_array
import numpy as np

arr = np.arange(100, dtype=float)
h = hash_array(arr)
# "a1b2c3d4e5f6..."  (32 hex chars)

# Works with torch tensors too
import torch
t = torch.ones(5, 5)
h = hash_array(t)
```

`hash_array` uses `hashlib.sha256` on the raw `.tobytes()` of the array. For PyTorch tensors it calls `.detach().cpu().numpy()` first.
