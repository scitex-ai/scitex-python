---
description: NaN-safe aggregation functions for PyTorch tensors — max, min, std, var, prod, cumulative prod/sum, argmax, argmin. Workarounds for missing NaN-safe ops in PyTorch core (pytorch/pytorch#61474).
---

# NaN-Safe Tensor Functions

PyTorch lacks built-in NaN-safe versions of several common aggregation operations. These functions fill that gap by replacing NaN values with appropriate neutral values before delegating to the native PyTorch ops.

All functions are accessible via `stx.torch.<name>`.

---

## nanmax

```python
nanmax(tensor, dim=None, keepdim=False)
```

Returns the maximum value, treating NaN as the smallest representable float
(`torch.finfo(tensor.dtype).min`).

**Parameters**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `tensor` | `torch.Tensor` | required | Input float tensor |
| `dim` | `int` or `None` | `None` | Dimension to reduce; `None` reduces over all elements |
| `keepdim` | `bool` | `False` | Whether to keep the reduced dimension |

**Returns** a scalar tensor when `dim=None`; a named tuple `(values, indices)` when `dim` is given (same as `torch.max`).

**Example**

```python
import scitex as stx
import torch

t = torch.tensor([1.0, float('nan'), 3.0, 2.0])

stx.torch.nanmax(t)
# tensor(3.)

stx.torch.nanmax(t, dim=0, keepdim=True)
# torch.return_types.max(values=tensor([3.]), indices=tensor([2]))

batch = torch.tensor([[1.0, float('nan')], [float('nan'), 4.0]])
stx.torch.nanmax(batch, dim=1)
# torch.return_types.max(values=tensor([1., 4.]), indices=tensor([0, 1]))
```

---

## nanmin

```python
nanmin(tensor, dim=None, keepdim=False)
```

Returns the minimum value, treating NaN as the largest representable float
(`torch.finfo(tensor.dtype).max`).

**Parameters** — same signature as `nanmax`.

**Example**

```python
t = torch.tensor([1.0, float('nan'), 3.0, 2.0])

stx.torch.nanmin(t)
# tensor(1.)

stx.torch.nanmin(t, dim=0)
# torch.return_types.min(values=tensor(1.), indices=tensor(0))
```

---

## nanvar

```python
nanvar(tensor, dim=None, keepdim=False)
```

Returns the variance, computed as `nanmean((x - nanmean(x))^2)`. NaN values
are excluded from both the mean and the variance computation. Uses
`torch.Tensor.nanmean` internally.

**Example**

```python
t = torch.tensor([1.0, float('nan'), 3.0, 5.0])

stx.torch.nanvar(t)
# tensor(2.6667)   # variance of [1, 3, 5]
```

---

## nanstd

```python
nanstd(tensor, dim=None, keepdim=False)
```

Returns the standard deviation. Computed as `sqrt(nanvar(...))`. NaN values
are excluded.

**Example**

```python
t = torch.tensor([1.0, float('nan'), 3.0, 5.0])

stx.torch.nanstd(t)
# tensor(1.6330)
```

---

## nanprod

```python
nanprod(tensor, dim=None, keepdim=False)
```

Returns the product, treating NaN as the multiplicative identity `1`. Uses
`tensor.nan_to_num(1)` then `torch.prod`.

**Example**

```python
t = torch.tensor([2.0, float('nan'), 3.0])

stx.torch.nanprod(t)
# tensor(6.)   # 2 * 1 * 3
```

---

## nancumsum

```python
nancumsum(tensor, dim=None, keepdim=False)
```

Returns the cumulative sum along a dimension, treating NaN as the additive
identity `0`. When `dim=None`, defaults to `dim=0`.

Note: `keepdim` is accepted for API consistency but has no effect (cumulative
operations always preserve shape).

**Example**

```python
t = torch.tensor([1.0, float('nan'), 3.0, 4.0])

stx.torch.nancumsum(t, dim=0)
# tensor([1., 1., 4., 8.])   # NaN treated as 0 at position 1
```

---

## nancumprod

```python
nancumprod(tensor, dim=None, keepdim=False)
```

Returns the cumulative product along a dimension, treating NaN as `1`. When
`dim=None`, defaults to `dim=0`.

**Example**

```python
t = torch.tensor([2.0, float('nan'), 3.0])

stx.torch.nancumprod(t, dim=0)
# tensor([2., 2., 6.])   # NaN treated as 1 at position 1
```

---

## nanargmax

```python
nanargmax(tensor, dim=None, keepdim=False)
```

Returns the index of the maximum value, treating NaN as the smallest
representable float. Uses `tensor.nan_to_num(min_value).argmax(...)`.

**Example**

```python
t = torch.tensor([1.0, float('nan'), 3.0, 2.0])

stx.torch.nanargmax(t)
# tensor(2)

stx.torch.nanargmax(t, dim=0)
# tensor(2)
```

---

## nanargmin

```python
nanargmin(tensor, dim=None, keepdim=False)
```

Returns the index of the minimum value, treating NaN as the largest
representable float. Uses `tensor.nan_to_num(max_value).argmin(...)`.

**Example**

```python
t = torch.tensor([1.0, float('nan'), 3.0, 2.0])

stx.torch.nanargmin(t)
# tensor(0)
```

---

## NaN replacement strategy summary

| Function | NaN replaced with | Rationale |
|----------|-------------------|-----------|
| `nanmax` / `nanargmax` | `finfo.min` | NaN cannot be the max |
| `nanmin` / `nanargmin` | `finfo.max` | NaN cannot be the min |
| `nanprod` / `nancumprod` | `1` | Multiplicative identity |
| `nancumsum` | `0` | Additive identity |
| `nanvar` / `nanstd` | excluded via `nanmean` | Mean-based computation |
