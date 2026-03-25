---
description: Compute the geometric median (L1 center) of a set of points along a specified dimension — a robust alternative to the arithmetic mean. Requires the geom_median package.
---

# Geometric Median

## geometric_median

Computes the geometric median (Weiszfeld L1 center) of a set of points along a specified dimension. The geometric median minimizes the sum of distances to all points, making it more robust to outliers than the arithmetic mean.

Decorated with `@torch_fn`: accepts NumPy arrays, PyTorch tensors, pandas DataFrames/Series, or plain Python lists; returns output in the same type as the first argument. Computation always runs on the best available device (CUDA if present, otherwise CPU).

Internally delegates to `geom_median.torch.compute_geometric_median`.

```python
geometric_median(xx, dim=-1) -> array_like
```

**Parameters**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `xx` | array_like | required | Input data. Each "slice" along `dim` is treated as one point in the set. |
| `dim` | int | `-1` | Dimension that indexes the individual points to aggregate. Negative indices are supported. |

**Output shape**

The output has the same shape as `xx` with the `dim` axis removed. For example:

| Input shape | `dim` | Output shape |
|-------------|-------|--------------|
| `(N, D)` | `-1` or `1` | `(N,)` |
| `(N, D)` | `0` | `(D,)` — median over N points each of dim D |
| `(B, N, D)` | `1` | `(B, D)` |

**Examples**

```python
import scitex as stx
import numpy as np

# 100 points in 10-dimensional space
X = np.random.randn(100, 10)

# Geometric median over the last dim (default dim=-1)
# Treats each of the 100 rows as a "point set of size 10"
median = stx.linalg.geometric_median(X)           # shape: (100,)

# More common use: median of 100 points, each with 10 features
# dim=0 collapses the 100-point axis → one 10-d median vector
median_of_points = stx.linalg.geometric_median(X, dim=0)   # shape: (10,)
```

```python
import scitex as stx
import numpy as np

# Robust center with outliers
rng = np.random.default_rng(0)
clean = rng.normal(size=(99, 3))
outlier = np.array([[100.0, 100.0, 100.0]])
data = np.vstack([clean, outlier])          # 100 x 3

mean_center = data.mean(axis=0)             # pulled toward outlier
geo_center  = stx.linalg.geometric_median(data, dim=0)   # robust
```

```python
import scitex as stx
import torch

# Tensor input returns tensor output
T = torch.randn(50, 8)
result = stx.linalg.geometric_median(T, dim=0)   # torch.Tensor, shape (8,)
```

**Notes**

- Requires `geom_median` to be installed (`pip install geom_median`).
- The function internally converts negative `dim` to a positive index via `xx.ndim + dim`.
- The function loops over the target dimension, collecting slices as individual points, then passes them to `compute_geometric_median`.
- For large inputs, computation is more expensive than `np.mean`; prefer `mean` when outlier robustness is not needed.
