---
name: stx.dsp.norm
description: Z-score and min-max normalization for multi-channel signals.
---

# stx.dsp.norm — Normalization

Source: `/home/ywatanabe/proj/scitex-python/src/scitex/dsp/norm.py`

Both functions are decorated with `@signal_fn`, accept NumPy arrays or PyTorch tensors, and return the same type. Requires `torch`.

## Functions

```python
x_z   = stx.dsp.norm.z(x, dim=-1)
x_mm  = stx.dsp.norm.minmax(x, amp=1.0, dim=-1, fn="mean")
```

### stx.dsp.norm.z

Z-score normalization: `(x - mean) / std` along `dim`.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `x` | ndarray / Tensor | required | Input signal |
| `dim` | int | `-1` | Dimension to normalize along |

Returns tensor with mean 0 and std 1 along `dim`.

### stx.dsp.norm.minmax

Min-max normalization scaled to `[-amp, amp]` using the max absolute value.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `x` | ndarray / Tensor | required | Input signal |
| `amp` | float | `1.0` | Output amplitude scale (result bounded by `[-amp, amp]`) |
| `dim` | int | `-1` | Dimension to normalize along |
| `fn` | str | `"mean"` | Unused (present for API compatibility) |

Implementation: divides by `max(|max|, |min|)` so the output fits in `[-amp, amp]`.

## Examples

```python
import scitex as stx

xx, tt, fs = stx.dsp.demo_sig(fs=256, t_sec=2)
# xx.shape: (8, 19, 512)

# Z-score normalize along time dimension
xx_z = stx.dsp.norm.z(xx, dim=-1)
# Each channel has mean ~0 and std ~1

# Min-max normalize to [-1, 1] range
xx_mm = stx.dsp.norm.minmax(xx, amp=1.0, dim=-1)

# Normalize along channel dimension (across channels per time point)
xx_ch = stx.dsp.norm.z(xx, dim=1)

# Normalize each batch independently
xx_b = stx.dsp.norm.z(xx, dim=-1)
```

## Common use cases

```python
import scitex as stx

xx, tt, fs = stx.dsp.demo_sig()

# Pre-normalize before bandpass filtering
xx_norm = stx.dsp.norm.z(xx)
xx_filt = stx.dsp.filt.bandpass(xx_norm, fs, [[4, 8]])

# Normalize after wavelet transform for visualization
pha, amp, freqs = stx.dsp.wavelet(xx, fs)
amp_norm = stx.dsp.norm.minmax(amp, amp=1.0)
```
