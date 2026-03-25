---
name: stx.dsp.reference
description: Common-average, random, and target channel re-referencing for EEG/LFP signals.
---

# stx.dsp.reference — Re-referencing

Source: `/home/ywatanabe/proj/scitex-python/src/scitex/dsp/reference.py`

All functions are decorated with `@torch_fn`, accept NumPy arrays or PyTorch tensors, and return the same type. They require `torch`.

Re-referencing is applied along the channel dimension (`dim=-2` by default, i.e., the second-to-last axis in a `(batch, chs, time)` tensor).

## Functions

```python
re_ref = stx.dsp.reference.common_average(x, dim=-2)
re_ref = stx.dsp.reference.random(x, dim=-2)
re_ref = stx.dsp.reference.take_reference(x, tgt_indi, dim=-2)
```

### stx.dsp.reference.common_average

Subtract the mean across all channels (common average reference), then z-score.

Formula: `(x - mean(x, dim)) / std(x, dim)`

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `x` | ndarray / Tensor | required | Signal `(batch, chs, time)` |
| `dim` | int | `-2` | Channel dimension |

### stx.dsp.reference.random

Subtract a random permutation of the channel data from the original.

Each call produces a different result (non-deterministic). Useful for data augmentation.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `x` | ndarray / Tensor | required | Signal `(batch, chs, time)` |
| `dim` | int | `-2` | Channel dimension |

### stx.dsp.reference.take_reference

Subtract a specific channel (or set of channels) from all channels.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `x` | ndarray / Tensor | required | Signal `(batch, chs, time)` |
| `tgt_indi` | int or slice | required | Index/indices of the reference channel(s) |
| `dim` | int | `-2` | Channel dimension |

## Examples

```python
import scitex as stx

xx, tt, fs = stx.dsp.demo_sig(n_chs=19, fs=256, t_sec=2)
# xx.shape: (8, 19, 512)

# Common average reference (standard for EEG)
xx_car = stx.dsp.reference.common_average(xx)
assert xx_car.shape == xx.shape

# Random reference (data augmentation)
xx_rand = stx.dsp.reference.random(xx)

# Reference to channel 0 (linked mastoid, for example)
xx_ref0 = stx.dsp.reference.take_reference(xx, tgt_indi=0)

# Reference to average of channels 17 and 18 (bilateral mastoids)
xx_bm = stx.dsp.reference.take_reference(xx, tgt_indi=slice(17, 19))
```

## EEG montage pipeline

```python
import scitex as stx
import numpy as np

# Load raw EEG (assumed shape: batch, chs, time)
xx, tt, fs = stx.dsp.demo_sig(sig_type="meg", n_chs=19, fs=256)

# 1. Re-reference to common average
xx = stx.dsp.reference.common_average(xx)

# 2. Bandpass filter to remove DC and high-frequency noise
xx = stx.dsp.filt.bandpass(xx, fs, np.array([[0.5, 80]]))

# 3. Z-score normalize
xx = stx.dsp.norm.z(xx)
```
