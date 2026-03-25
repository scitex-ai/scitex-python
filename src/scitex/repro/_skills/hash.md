---
name: repro-hash
description: Compute a deterministic fingerprint of a numpy array with hash_array() for integrity verification and deduplication.
---

# Array Hashing

## hash_array

Compute a deterministic hex string fingerprint of a numpy array.

```python
hash_array(arr: np.ndarray) -> str
```

Uses SHA-256 of the array's byte representation. Same array content always produces the same hash regardless of variable name or process.

```python
import numpy as np
import scitex as stx

arr = np.array([1.0, 2.0, 3.0])
h = stx.repro.hash_array(arr)
print(h)  # e.g., 'a1b2c3d4...'  (64 hex chars)

# Verify that two datasets are identical
assert stx.repro.hash_array(data_a) == stx.repro.hash_array(data_b)
```

Useful for:
- Verifying that a preprocessing step is deterministic
- Deduplicating cached computation results
- Naming cache files by content hash

```python
import scitex as stx
import numpy as np

features = compute_expensive_features(raw_data)
cache_key = stx.repro.hash_array(features)
cache_path = f"cache/{cache_key}.npy"

if not os.path.exists(cache_path):
    stx.io.save(features, cache_path)
```
