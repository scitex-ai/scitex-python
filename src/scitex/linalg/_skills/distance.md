---
name: linalg-distance
description: Euclidean distance (point-to-point and pairwise) via euclidean_distance / edist and cdist. Use when computing distances between vectors or full pairwise distance matrices.
---

# Distance Functions

## euclidean_distance / edist

Computes Euclidean distance between two arrays along a specified axis. `edist` is an alias for `euclidean_distance`.

Decorated with `@numpy_fn`: accepts NumPy arrays, PyTorch tensors, pandas DataFrames/Series, or plain Python lists; returns output in the same type as the first argument.

```python
euclidean_distance(uu, vv, axis=0) -> array_like
```

**Parameters**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `uu` | array_like | required | First input array |
| `vv` | array_like | required | Second input array |
| `axis` | int | `0` | Axis along which to compute the distance |

**Shape rules**

- Both arrays are passed through `np.atleast_1d` before processing.
- `uu.shape[axis]` must equal `vv.shape[axis]`; a `ValueError` is raised otherwise.
- The distance is computed element-wise after broadcasting along all other axes, yielding an output shape equal to the non-axis dimensions of `uu` and `vv` combined.

**Examples**

```python
import scitex as stx
import numpy as np

# Two 1-D vectors — scalar result
a = np.array([0.0, 0.0])
b = np.array([3.0, 4.0])
stx.linalg.euclidean_distance(a, b)   # 5.0
stx.linalg.edist(a, b)                # same, alias

# Two 2-D arrays (one row each), axis=0
A = np.array([[1.0, 2.0]])
B = np.array([[4.0, 6.0]])
stx.linalg.euclidean_distance(A, B, axis=0)   # array([[5.]])

# Works with PyTorch tensors — returns tensor
import torch
stx.linalg.edist(torch.tensor([1., 0.]), torch.tensor([0., 1.]))  # tensor(1.4142...)

# Works with plain lists
stx.linalg.edist([1, 0, 0], [0, 1, 0])   # ~1.414 (list input → list scalar)
```

---

## cdist

Computes pairwise distances between all rows in two 2-D arrays. This is a thin `@wrap` passthrough to `scipy.spatial.distance.cdist`, exposing the full scipy interface with preserved function metadata.

```python
cdist(XA, XB, metric='minkowski', **kwargs) -> np.ndarray
```

Full parameter documentation is inherited from `scipy.spatial.distance.cdist`.

**Common usage**

| `metric` value | Distance computed |
|----------------|-------------------|
| `'euclidean'` (default via minkowski p=2) | Standard L2 |
| `'cosine'` | 1 − cosine similarity |
| `'cityblock'` | L1 / Manhattan |
| `'chebyshev'` | L∞ |

**Examples**

```python
import scitex as stx
import numpy as np

X = np.random.randn(100, 10)   # 100 samples, 10 features
Y = np.random.randn(50, 10)    #  50 samples, 10 features

# Full pairwise matrix: shape (100, 50)
D = stx.linalg.cdist(X, Y)

# Explicitly Euclidean
D_euc = stx.linalg.cdist(X, Y, metric='euclidean')

# Cosine distance
D_cos = stx.linalg.cdist(X, Y, metric='cosine')

# Nearest neighbor index for each row in X
nn_idx = np.argmin(D_euc, axis=1)   # shape (100,)
```

---

## Choosing between edist and cdist

| Situation | Function |
|-----------|----------|
| Distance between two individual vectors | `edist` / `euclidean_distance` |
| Distance between rows of two matrices (all pairs) | `cdist` |
| Non-Euclidean metric (cosine, L1, …) | `cdist` with `metric=` |
| Input is a tensor or DataFrame | `edist` / `euclidean_distance` (handles type conversion) |
