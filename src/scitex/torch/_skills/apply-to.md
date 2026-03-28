---
description: apply_to — apply an arbitrary Python/PyTorch function along a specified tensor dimension by temporarily permuting and unbinding.
---

# apply_to — Apply a Function Along a Tensor Dimension

`apply_to` lets you apply any callable to each 1-D slice of a tensor along
a chosen dimension. This is useful when a function does not natively support
a `dim` keyword argument or when you need non-standard reduction behaviour.

```python
apply_to(fn, x, dim) -> torch.Tensor
```

**Parameters**

| Parameter | Type | Description |
|-----------|------|-------------|
| `fn` | `callable` | Function that accepts a 1-D tensor and returns a tensor (or scalar). Applied independently to each slice along `dim`. |
| `x` | `torch.Tensor` | Input tensor of any shape and dtype. |
| `dim` | `int` | Dimension along which to apply `fn`. Use `-1` for the last dimension (no permutation performed). |

**Returns** a tensor with the same number of dimensions as `x`. The size of
`dim` in the output depends on the shape of what `fn` returns.

**How it works**

1. If `dim != -1`, the last dimension and `dim` are swapped via `permute`.
2. The tensor is flattened to 2-D `(batch, last_dim)`.
3. `fn` is called on each row independently; results are stacked back.
4. The tensor is reshaped to match the original shape (with the function's
   output size replacing the original `dim` size).
5. If a permutation was applied, it is reversed.

**Important**: `fn` receives a 1-D tensor (one row of the flattened view).
The output length of `fn` determines the new size along `dim`.

---

## Examples

### Basic reduction along a dimension

```python
import scitex as stx
import torch

x = torch.randn(2, 3, 4)

# Apply Python's built-in sum along dim 1 — result shape: (2, 1, 4)
result = stx.torch.apply_to(sum, x, dim=1)
result.shape
# torch.Size([2, 1, 4])
```

### Custom function that returns a scalar per slice

```python
# Median along the last dimension
result = stx.torch.apply_to(lambda v: v.median().unsqueeze(0), x, dim=-1)
result.shape
# torch.Size([2, 3, 1])
```

### Using a torch function that lacks a dim argument

```python
# Hypothetical custom normalizer
def l2_normalize(v):
    return v / v.norm()

result = stx.torch.apply_to(l2_normalize, x, dim=2)
result.shape
# torch.Size([2, 3, 4])   # same shape; fn returns same-length tensor
```

---

## Constraints and edge cases

- `fn` must return a tensor (not a plain Python float) for `torch.stack` to
  work. Wrap scalars in `.unsqueeze(0)` or use `torch.tensor([value])`.
- For large tensors the Python-level loop over `torch.unbind` slices can be
  slow. Prefer native torch ops with `dim` arguments when available.
- `dim=-1` skips the permutation step entirely, which is slightly faster.
- The function does not in-place modify `x`.
