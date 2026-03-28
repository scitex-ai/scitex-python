---
name: stx.linalg
description: Linear algebra utilities — distance metrics, geometric median, cosine similarity, NaN-aware norm, vector projection, and coordinate reconstruction. Use when computing distances between arrays, finding robust centroids, or working with vector geometry.
user-invocable: false
---

# stx.linalg

Linear algebra utility functions for scientific computing. Accessed via `import scitex as stx` then `stx.linalg.<function>`.

Most functions accept NumPy arrays, PyTorch tensors, pandas DataFrames/Series, or plain Python lists, and return output in the same type as the first argument.

## Public API

```python
import scitex as stx

# Distance
stx.linalg.euclidean_distance(uu, vv, axis=0)
stx.linalg.edist(uu, vv, axis=0)          # alias for euclidean_distance
stx.linalg.cdist(XA, XB, metric='minkowski', **kwargs)

# Robust centroid
stx.linalg.geometric_median(xx, dim=-1)

# Vector operations
stx.linalg.cosine(v1, v2)
stx.linalg.nannorm(v, axis=-1)
stx.linalg.rebase_a_vec(v, v_base)
stx.linalg.three_line_lengths_to_coords(aa, bb, cc)
```

## Sub-skills

### Distance Metrics
- [distance.md](distance.md) — `euclidean_distance`, `edist`, `cdist`: point-to-point and full pairwise distance matrices, with type-transparent NumPy conversion

### Geometric Median
- [geometric-median.md](geometric-median.md) — `geometric_median`: L1 robust centroid via `geom_median.torch`, works on tensors and arrays, CUDA-accelerated

### Vector Operations
- [vector-ops.md](vector-ops.md) — `cosine`, `nannorm`, `rebase_a_vec`, `three_line_lengths_to_coords`: NaN-safe similarity, norm, projection, and triangle coordinate reconstruction
