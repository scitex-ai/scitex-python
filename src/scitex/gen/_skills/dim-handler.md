---
description: DimHandler class in stx.gen — flattens non-target dimensions into a single batch dimension, performs computations on selected dimensions, then restores the original shape. Works with both torch.Tensor and numpy.ndarray.
---

# DimHandler

`DimHandler` lets you operate on arbitrary selected dimensions of a multi-dimensional tensor or array without writing manual reshape/permute code. It stores the geometry from `fit()` and uses it to reverse the transformation in `unfit()`.

> **Note:** Requires `torch`. `stx.gen.DimHandler` is `None` when torch is not installed.

```python
from scitex.gen import DimHandler
```

---

## How it works

Given an input with shape `(d0, d1, d2, d3, d4, d5)` and `keepdims=[0, 2, 5]`:

1. `fit()` permutes to `(non-kept dims..., kept dims...)` → `(d1, d3, d4, d0, d2, d5)`
2. Flattens the leading non-kept axes → `(d1*d3*d4, d0, d2, d5)` — i.e. `(40, 1, 3, 6)` for `(1,2,3,4,5,6)` shaped input
3. You perform your computation on the kept-dim axes
4. `unfit()` restores the first (batch) axis to its original shape `(d1, d3, d4, ...)`

---

## Constructor

```python
DimHandler()
```

No parameters. State is stored after calling `fit()`.

---

## fit

```python
dh.fit(x, keepdims=[]) -> tensor / array
```

Reshapes `x` by flattening all dimensions **not** in `keepdims` into the leading batch dimension. The kept dimensions are moved to the trailing axes in their original relative order.

| Parameter | Description |
|-----------|-------------|
| `x` | `torch.Tensor` or `numpy.ndarray` |
| `keepdims` | List of dimension indices to keep. Negative indices supported. |

Returns the reshaped array. Also records `shape_fit`, `n_non_keepdims`, `n_keepdims` on the handler.

---

## unfit

```python
dh.unfit(y) -> tensor / array
```

Restores the first (batch) dimension back to the original non-kept dimensions. The trailing dimensions of `y` may differ from the original (e.g. after a reduction), and `unfit` handles this correctly.

| Parameter | Description |
|-----------|-------------|
| `y` | Output after your computation. Must have the same batch size as returned by `fit`. |

---

## Examples

### Example 1 — lossless round-trip

```python
import torch
from scitex.gen import DimHandler

dh = DimHandler()
x = torch.rand(1, 2, 3, 4, 5, 6)
print(x.shape)   # torch.Size([1, 2, 3, 4, 5, 6])

x_fit = dh.fit(x, keepdims=[0, 2, 5])
print(x_fit.shape)  # torch.Size([40, 1, 3, 6])
# 40 = 2*4*5 (the non-kept dims)

x_restored = dh.unfit(x_fit)
print(x_restored.shape)  # torch.Size([2, 4, 5, 1, 3, 6])
# Note: original dim order is not restored; non-kept dims come first
```

### Example 2 — computation that reduces a kept dimension

```python
dh = DimHandler()
x = torch.rand(1, 2, 3, 4, 5, 6)

x_fit = dh.fit(x, keepdims=[0, 2, 5])
print(x_fit.shape)   # torch.Size([40, 1, 3, 6])

# Reduce over dim=-2 (the "3" kept dimension)
y = x_fit.mean(axis=-2)
print(y.shape)  # torch.Size([40, 1, 6])

y_restored = dh.unfit(y)
print(y_restored.shape)  # torch.Size([2, 4, 5, 1, 6])
```

### Example 3 — numpy array

```python
import numpy as np
from scitex.gen import DimHandler

dh = DimHandler()
x = np.random.rand(2, 3, 4)

x_fit = dh.fit(x, keepdims=[1])
print(x_fit.shape)  # (8, 3)  — 2*4 batch, 3 kept

result = x_fit.sum(axis=-1, keepdims=True)
print(result.shape)  # (8, 1)

restored = dh.unfit(result)
print(restored.shape)  # (2, 4, 1)
```

---

## Notes

- `DimHandler` is **stateful**: a single instance should only be used for one `fit`/`unfit` pair at a time. Create a new instance for each independent operation.
- Negative keepdim indices are normalized before processing.
- The restored shape places non-kept dimensions first; the original permutation order is **not** restored.
