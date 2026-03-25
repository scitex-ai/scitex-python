---
description: Add Gaussian, white, pink, or brown noise to signals.
---

# stx.dsp.add_noise — Noise Addition

Source: `/home/ywatanabe/proj/scitex-python/src/scitex/dsp/add_noise.py`

All functions are decorated with `@signal_fn`, accept NumPy arrays or PyTorch tensors, and return the same type. Requires `torch`.

## Functions

```python
noisy = stx.dsp.add_noise.gauss(x, amp=1.0)
noisy = stx.dsp.add_noise.white(x, amp=1.0)
noisy = stx.dsp.add_noise.pink(x, amp=1.0, dim=-1)
noisy = stx.dsp.add_noise.brown(x, amp=1.0, dim=-1)
```

### Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `x` | ndarray / Tensor | required | Input signal |
| `amp` | float | `1.0` | Noise amplitude (scale factor) |
| `dim` | int | `-1` | Dimension along which to generate correlated noise (pink, brown only) |

### Returns

Signal with noise added, same shape and type as input.

## Noise types

| Function | Type | Spectrum |
|----------|------|---------|
| `gauss` | Gaussian | White (flat), samples from `N(0, amp)` |
| `white` | Uniform | White (flat), samples from `U(-amp, amp)` |
| `pink` | 1/f noise | Pink spectrum: power `~ 1/f` |
| `brown` | Brownian | Red spectrum: cumulative sum of uniform, then min-max normalized |

## Examples

```python
import scitex as stx

xx, tt, fs = stx.dsp.demo_sig(fs=128, t_sec=1)

# Add different noise types
xx_gauss = stx.dsp.add_noise.gauss(xx, amp=0.5)
xx_white  = stx.dsp.add_noise.white(xx, amp=0.5)
xx_pink   = stx.dsp.add_noise.pink(xx, amp=0.5)
xx_brown  = stx.dsp.add_noise.brown(xx, amp=0.5)

# Inspect noise alone
noise = stx.dsp.add_noise.pink(xx, amp=1.0) - xx
```

## Data augmentation use case

```python
import scitex as stx
import numpy as np

xx, tt, fs = stx.dsp.demo_sig(batch_size=8, fs=256, t_sec=2)

# Augment by mixing noise types with different amplitudes
xx_aug_1 = stx.dsp.add_noise.gauss(xx, amp=0.1)   # mild Gaussian
xx_aug_2 = stx.dsp.add_noise.pink(xx, amp=0.3)    # realistic 1/f noise

augmented = np.concatenate([xx, xx_aug_1, xx_aug_2], axis=0)
# augmented.shape: (24, 19, 512)
```
