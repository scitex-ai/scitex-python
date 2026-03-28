---
name: stx.repro
description: Reproducibility utilities for random state management, ID generation, timestamps, and array hashing.
---

# stx.repro — Skills Index

Deterministic random state management across all ML frameworks, unique experiment ID generation, timestamp utilities, and array hashing for change detection.

## Sub-skills

| File | Description |
|------|-------------|
| [random-state-manager.md](random-state-manager.md) | RandomStateManager, named generators, verify(), checkpoint/restore, temporary_seed |
| [id-timestamp-hash.md](id-timestamp-hash.md) | gen_id, gen_timestamp, hash_array |

## Quick Reference

```python
from scitex.repro import RandomStateManager, gen_id, gen_timestamp, hash_array

rng = RandomStateManager(seed=42)
data = rng.get_np_generator("data").random(100)
rng.verify(data, "train_data")

eid = gen_id()          # "2025Y-05M-31D-12h30m45s_a3Bc9xY2"
ts  = gen_timestamp()   # "2025-0531-1230"
h   = hash_array(data)  # 32-char SHA256 hex
```
