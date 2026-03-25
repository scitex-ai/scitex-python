---
name: gen-numeric-utils
description: Numeric helper functions in stx.gen — rounding to nearest even/odd integer, tensor rank conversion, symmetric log transform, named-dimension transpose, and numeric sequence helpers (connect_nums, float_linspace).
---

# Numeric Utilities

Small but precise helpers for numeric type coercion, transforms, and array operations.

---

## to_even

Converts any real number to the nearest even integer **less than or equal** to itself (floor-then-even).

```python
to_even(n: int | float) -> int
```

| Input | Output |
|-------|--------|
| `5` | `4` |
| `6` | `6` |
| `3.7` | `2` |
| `-2.3` | `-4` |
| `-0.1` | `-2` |

Raises `ValueError` for `NaN`, `OverflowError` for `±inf`, `TypeError` for strings.

```python
import scitex as stx

stx.gen.to_even(101)   # 100
stx.gen.to_even(200)   # 200
stx.gen.to_even(7.9)   # 6
```

**Common use case:** Ensure an FFT window length is even.

```python
n_fft = stx.gen.to_even(int(fs * 0.025))  # 25 ms window, forced even
```

---

## to_odd

Converts any real number to the nearest odd integer **less than or equal** to itself.

```python
to_odd(n: int | float) -> int
```

| Input | Output |
|-------|--------|
| `6` | `5` |
| `7` | `7` |
| `5.8` | `5` |

```python
kernel_size = stx.gen.to_odd(int(fs * 0.010))  # 10 ms kernel, forced odd
```

**Implementation:** `int(n) - ((int(n) + 1) % 2)` — compact and branch-free.

---

## to_rank

Converts a 1-D tensor to its rank vector (1-based).

```python
to_rank(tensor, method="average") -> torch.Tensor
```

> **Note:** Requires `torch`. Returns `None` when torch is not installed.

| Parameter | Default | Description |
|-----------|---------|-------------|
| `tensor` | required | 1-D `torch.Tensor` (or array via `@torch_fn`) |
| `method` | `"average"` | Tie-breaking: `"average"` assigns the mean rank to tied values |

```python
import torch
import scitex as stx

x = torch.tensor([3.0, 1.0, 2.0, 1.0])
stx.gen.to_rank(x)
# tensor([4., 1.5, 3., 1.5])  — tied values at positions 1 and 3 get average rank
```

---

## symlog

Symmetric log transform: linear near zero, logarithmic for large magnitudes. Preserves sign.

```python
symlog(x, linthresh=1.0) -> array-like
```

| Parameter | Default | Description |
|-----------|---------|-------------|
| `x` | required | Input array or tensor |
| `linthresh` | `1.0` | Width of the linear region around zero |

Formula: `sign(x) * log1p(|x| / linthresh)`

```python
import numpy as np
import scitex as stx

x = np.array([-1000, -1, 0, 1, 1000])
stx.gen.symlog(x, linthresh=1.0)
# array([-6.908,  -0.693,  0., 0.693, 6.908])
```

**Use case:** Plotting neural signals or financial data with large dynamic range and values near zero.

---

## transpose

Name-based dimension transposition for arrays. Accepts dimension name arrays instead of integer indices.

```python
transpose(arr_like, src_dims, tgt_dims) -> np.ndarray
```

Decorated with `@numpy_fn` — accepts torch.Tensor or list inputs.

| Parameter | Description |
|-----------|-------------|
| `arr_like` | Input array |
| `src_dims` | Array of dimension names in current order |
| `tgt_dims` | Array of dimension names in desired order (same elements, different order) |

`src_dims` and `tgt_dims` must contain identical sets of names.

```python
import numpy as np
import scitex as stx

x = np.random.rand(2, 3, 4)
src = np.array(["batch", "time", "freq"])
tgt = np.array(["freq", "batch", "time"])

y = stx.gen.transpose(x, src, tgt)
print(y.shape)  # (4, 2, 3)
```

---

## connect_nums

Joins an iterable of values into a hyphen-separated string.

```python
connect_nums(nums: Iterable) -> str
```

```python
import scitex as stx

stx.gen.connect_nums((0, 0))      # "0-0"
stx.gen.connect_nums((1, 2, 3))   # "1-2-3"
stx.gen.connect_nums(("a", "b"))  # "a-b"
```

**Use case:** Building unique filename stems from parameter tuples.

```python
fname = f"result_{stx.gen.connect_nums((subject_id, session_id, run))}.csv"
# "result_3-2-1.csv"
```

---

## float_linspace

Generates evenly spaced floats over an interval. Similar to `np.linspace` but guarantees step-based arithmetic (avoids floating-point drift in edge cases).

```python
float_linspace(start: float, stop: float, num_points: int) -> np.ndarray
```

```python
import scitex as stx

stx.gen.float_linspace(0, 1, 5)
# array([0.  , 0.25, 0.5 , 0.75, 1.  ])

stx.gen.float_linspace(1, 2, 3)
# array([1. , 1.5, 2. ])
```

When `num_points < 2`, returns `[start]` for `num_points == 1` or `[start, stop]` for `num_points == 2`.
