---
name: stx.dsp.hilbert
description: Hilbert transform returning instantaneous phase and amplitude envelope.
---

# stx.dsp.hilbert — Analytic Signal

Source: `/home/ywatanabe/proj/scitex-python/src/scitex/dsp/_hilbert.py`

## Signature

```python
phase, amplitude = stx.dsp.hilbert(x, dim=-1)
```

Computes the analytic signal via the Hilbert transform using `scitex.nn._Hilbert`. Both outputs have the same shape as `x`.

### Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `x` | ndarray / Tensor | required | Input signal, shape `(batch, chs, time)` |
| `dim` | int | `-1` | Dimension along which to apply the transform |

### Returns

- `phase`: instantaneous phase in radians, same shape as `x`
- `amplitude`: amplitude envelope (always non-negative), same shape as `x`

Decorated with `@signal_fn`: accepts NumPy arrays, PyTorch tensors, or DataFrames; returns the same type.

## Examples

```python
import scitex as stx

xx, tt, fs = stx.dsp.demo_sig(sig_type="chirp", t_sec=1.0, fs=400)
# xx.shape: (8, 19, 400)

phase, amplitude = stx.dsp.hilbert(xx)
# phase.shape:     (8, 19, 400)  — values in [-pi, pi]
# amplitude.shape: (8, 19, 400)  — non-negative envelope

# Plot signal and envelope for first batch/channel
import matplotlib.pyplot as plt
fig, axes = plt.subplots(2, 1, sharex=True)
axes[0].plot(tt, xx[0, 0], label="signal")
axes[0].plot(tt, amplitude[0, 0], label="envelope")
axes[0].legend()
axes[1].plot(tt, phase[0, 0], label="phase [rad]")
axes[1].legend()
```

## PAC preprocessing pipeline

`hilbert` is used internally by `pac` and `detect_ripples`, but you can also call it directly for custom phase-amplitude analyses:

```python
import scitex as stx
import numpy as np

xx, tt, fs = stx.dsp.demo_sig(fs=512, t_sec=4)

# Extract theta phase
theta = stx.dsp.filt.bandpass(xx, fs, np.array([[4, 8]]))
theta_phase, _ = stx.dsp.hilbert(theta)

# Extract gamma amplitude
gamma = stx.dsp.filt.bandpass(xx, fs, np.array([[32, 80]]))
_, gamma_amp = stx.dsp.hilbert(gamma)

# theta_phase and gamma_amp are ready for coupling analysis
```
