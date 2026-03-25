---
name: stx.nn - Utility Layers
description: Lightweight nn.Module helpers — SpatialAttention, TransposeLayer, and the standalone GaussianFilter (_GaussianFilter.py). These are building blocks for larger architectures.
---

# stx.nn — Utility Layers

---

## SpatialAttention

Computes a learned spatial (channel-wise) attention weight and multiplies the input by it.  Used inside `BHead` in the BNet architectures.

```python
import torch
import scitex as stx

layer = stx.nn.SpatialAttention(n_chs_in=19)
# n_chs_in: int — number of input channels

x = torch.randn(8, 19, 1024)   # (batch, n_chs, seq_len)
y = layer(x)                    # (8, 19, 1024) — same shape as input

# Mechanism:
#   1. AdaptiveAvgPool1d(1)  →  (batch, n_chs, 1)  — global average per channel
#   2. Conv1d(n_chs_in, 1, kernel_size=1)  →  (batch, 1, 1)  — scalar weight
#   3. Return  scalar_weight * x_orig   (broadcast over time dim)
```

This is a simplified attention that produces a single scalar gate rather than per-channel weights.

---

## TransposeLayer

Wraps `torch.Tensor.transpose` as an `nn.Module` so it can be used inside `nn.Sequential`.

```python
layer = stx.nn.TransposeLayer(axis1=1, axis2=2)
# axis1, axis2: int — the two dimensions to swap

x = torch.randn(8, 19, 1024)
y = layer(x)   # (8, 1024, 19)
```

---

## GaussianFilter (from _GaussianFilter.py)

A separate, radius-based Gaussian smoothing layer (different from `GaussianFilter` in `_Filters.py`).

```python
layer = stx.nn.GaussianFilter   # NOTE: this name resolves to _Filters.py's version
                                  # (imported last in __init__.py)

# To use _GaussianFilter.py's version directly:
from scitex.nn._GaussianFilter import GaussianFilter as GaussianFilterRadius

layer = GaussianFilterRadius(
    radius=5,    # half-width in samples; kernel_size = 2 * radius + 1
    sigma=None,  # if None, sigma = radius / 2
)

x = torch.randn(8, 19, 1024)
y = layer(x)   # same shape as input (padding=radius preserves length)

# Works on 1D, 2D, or 3D inputs:
#   1D: unsqueezed to (1, 1, seq_len)
#   2D: unsqueezed to (batch, 1, seq_len)
#   3D: (batch, n_chs, seq_len) — applied with grouped convolution
```

### Comparison of the two GaussianFilter classes

| | `_Filters.GaussianFilter` | `_GaussianFilter.GaussianFilter` |
|---|---|---|
| Constructor | `GaussianFilter(sigma)` | `GaussianFilter(radius, sigma=None)` |
| Kernel size | `sigma * 6` | `2 * radius + 1` |
| Output shape | `(batch, n_chs, 1, seq_len)` — adds filter dim | `(batch, n_chs, seq_len)` — preserves shape |
| Exported as | `stx.nn.GaussianFilter` | Must import from `_GaussianFilter` directly |
| Normalisation | Sum = 1 | Normalised Gaussian PDF then divided by sum |

---

## SwapLayer and ReshapeLayer

These are internal helper layers used inside `MNet1000`. They are also exported from `stx.nn`.

```python
# SwapLayer — identical to TransposeLayer(1, 2)
swap = stx.nn.SwapLayer()
y = swap(x)   # x.transpose(1, 2)

# ReshapeLayer — flatten all dims except batch
reshape = stx.nn.ReshapeLayer()
y = reshape(x)   # x.reshape(len(x), -1)
```
