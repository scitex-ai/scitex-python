---
description: Tensor and array normalization functions in stx.gen — z-score, min-max, NaN-safe variants, unbiasing, percentile clipping. All accept both torch.Tensor and numpy.ndarray (via @torch_fn decorator). Optional caching layer for repeated operations.
---

# Tensor Normalization

All functions accept `torch.Tensor` or `numpy.ndarray` thanks to the `@torch_fn` decorator. NumPy arrays are converted to tensors, computed, and returned as tensors (or arrays if the input was NumPy). All normalization is **along a single dimension** by default.

> **Note:** Requires `torch`. Functions are `None` when torch is not installed.

---

## to_z

Z-score normalization: zero mean, unit variance along a dimension.

```python
to_z(x, axis=-1, dim=None, device="cuda") -> torch.Tensor
```

| Parameter | Default | Description |
|-----------|---------|-------------|
| `x` | required | Input tensor or array |
| `dim` | `None` | Preferred: dimension along which to normalize |
| `axis` | `-1` | Numpy compat alias for `dim` |
| `device` | `"cuda"` | Computation device (auto-fallback to cpu) |

```python
import scitex as stx
import torch

x = torch.randn(4, 100)
z = stx.gen.to_z(x, dim=-1)
# z.mean(dim=-1) ≈ 0, z.std(dim=-1) ≈ 1
```

---

## to_nanz

Z-score normalization with NaN handling using `torch.nanmean` and `scitex.torch.nanstd`.

```python
to_nanz(x, axis=-1, dim=None, device="cuda") -> torch.Tensor
```

Same signature as `to_z`. NaN values in `x` are skipped when computing mean and std; they remain NaN in the output.

```python
x = torch.tensor([1.0, 2.0, float("nan"), 4.0])
z = stx.gen.to_nanz(x, dim=0)
```

---

## to_01

Min-max normalization to the [0, 1] range.

```python
to_01(x, axis=-1, dim=None, device="cuda") -> torch.Tensor
```

Uses `1e-8` epsilon to avoid division by zero when min == max.

```python
x = torch.tensor([2.0, 4.0, 6.0, 8.0])
scaled = stx.gen.to_01(x, dim=0)
# tensor([0.000, 0.333, 0.667, 1.000])
```

---

## to_nan01

Min-max normalization with NaN handling using `torch.nanmin` / `torch.nanmax`.

```python
to_nan01(x, axis=-1, dim=None, device="cuda") -> torch.Tensor
```

NaN values remain NaN in the output; min/max are computed over non-NaN values.

---

## unbias

Removes bias (mean or min) from a tensor along a dimension.

```python
unbias(x, axis=-1, dim=None, fn="mean", device="cuda") -> torch.Tensor
```

| `fn` value | Operation |
|------------|-----------|
| `"mean"` | Subtracts `x.mean(dim=dim, keepdims=True)` |
| `"min"` | Subtracts `x.min(dim=dim, keepdims=True)[0]` |

```python
x = torch.tensor([[1.0, 2.0, 3.0], [10.0, 20.0, 30.0]])
debiased = stx.gen.unbias(x, dim=-1, fn="mean")
# Each row now has mean 0
```

---

## clip_perc

Clips values to the range [lower percentile, upper percentile] along a dimension.

```python
clip_perc(
    x,
    lower_perc=2.5,
    upper_perc=97.5,
    low=None,
    high=None,
    axis=-1,
    dim=None,
    device="cuda",
) -> torch.Tensor
```

| Parameter | Default | Description |
|-----------|---------|-------------|
| `lower_perc` | `2.5` | Lower bound percentile (0–100) |
| `upper_perc` | `97.5` | Upper bound percentile (0–100) |
| `low` | `None` | Alternative name for `lower_perc` |
| `high` | `None` | Alternative name for `upper_perc` |

```python
x = torch.randn(1000)
clipped = stx.gen.clip_perc(x, lower_perc=5, upper_perc=95, dim=0)
```

---

## Caching Layer (norm_cache)

`_norm_cache.py` provides optional caching for repeated normalizations of identical data. By default, it **auto-patches** `to_z` and `to_01` in `scitex.gen` when the environment variable `SCITEX_CACHE_NORM=true` (the default).

### Cache control functions

```python
from scitex.gen._norm_cache import configure_norm_cache, clear_norm_cache, get_norm_cache_info

# Tune cache
configure_norm_cache(enabled=True, max_size=128, verbose=True)

# Inspect
info = get_norm_cache_info()
# {'enabled': True, 'max_size': 128, 'current_size': 3, 'operations': ['z-score', ...]}

# Clear all cached results
clear_norm_cache()
```

### Cached variants

```python
from scitex.gen._norm_cache import to_z_cached, to_01_cached

# Drop-in replacements with LRU-style weak-reference caching
z = to_z_cached(x, dim=-1)
scaled = to_01_cached(x, dim=0)
```

Cache keys are based on array shape, dtype, device, and sampled values. The cache uses `weakref.WeakValueDictionary` so it does not prevent garbage collection.

### Disable caching

```
SCITEX_CACHE_NORM=false python my_script.py
```
