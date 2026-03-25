---
name: stx.dsp.filt
description: Bandpass, bandstop, lowpass, highpass, and Gaussian filters for multi-channel signals.
---

# stx.dsp.filt — Filtering

Source: `/home/ywatanabe/proj/scitex-python/src/scitex/dsp/filt.py`

All filter functions are decorated with `@signal_fn`, which means they accept NumPy arrays, PyTorch tensors, or pandas DataFrames and return the same type. Input shape must be `(batch_size, n_chs, seq_len)` or compatible broadcastable form.

Filters are implemented as PyTorch neural network modules from `scitex.nn._Filters`. They require `torch`.

## Function Signatures

```python
stx.dsp.filt.bandpass(x, fs, bands, t=None)
stx.dsp.filt.bandstop(x, fs, bands, t=None)
stx.dsp.filt.lowpass(x, fs, cutoffs_hz, t=None)
stx.dsp.filt.highpass(x, fs, cutoffs_hz, t=None)
stx.dsp.filt.gauss(x, sigma, t=None)
```

### Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `x` | ndarray / Tensor | Input signal, shape `(batch, chs, time)` |
| `fs` | float | Sampling frequency in Hz |
| `bands` | array `(n_bands, 2)` | `[[low_hz, high_hz], ...]` for bandpass/bandstop |
| `cutoffs_hz` | array `(n_bands,)` | Cutoff frequencies for lowpass/highpass |
| `sigma` | float | Gaussian kernel width in samples (standard deviations) |
| `t` | ndarray or None | Optional time vector; if given, also returned |

### Return values

- Without `t`: filtered signal, same shape and type as input
- With `t`: `(filtered_signal, time_vector)` — time vector is unchanged

## Examples

```python
import scitex as stx
import numpy as np

xx, tt, fs = stx.dsp.demo_sig(sig_type="periodic", fs=1024, t_sec=1)
# xx.shape: (8, 19, 1024)

# Single band: [[low_hz, high_hz]]
BANDS = np.array([[80, 310]])

# Bandpass 80-310 Hz
x_bp = stx.dsp.filt.bandpass(xx, fs, BANDS)

# Bandstop 80-310 Hz (notch)
x_bs = stx.dsp.filt.bandstop(xx, fs, BANDS)

# Lowpass at 80 Hz
x_lp = stx.dsp.filt.lowpass(xx, fs, BANDS[:, 0])

# Highpass at 310 Hz
x_hp = stx.dsp.filt.highpass(xx, fs, BANDS[:, 1])

# Gaussian smoothing (sigma=3 samples)
x_g = stx.dsp.filt.gauss(xx, sigma=3)

# With time vector returned
x_bp, t_bp = stx.dsp.filt.bandpass(xx, fs, BANDS, t=tt)
```

## Multi-band filtering

`bandpass` and `bandstop` accept multiple bands at once. The output gains an extra dimension for each band:

```python
BANDS = np.array([[4, 8], [8, 13], [13, 30]])  # theta, alpha, beta
x_multi = stx.dsp.filt.bandpass(xx, fs, BANDS)
# x_multi.shape: (8, 19, 3, 1024)  — extra dim for n_bands
```

## EEG use case

```python
# Ripple band detection preprocessing
ripple_bands = np.array([[80, 140]])
x_ripple = stx.dsp.filt.bandpass(xx, fs, ripple_bands)

# Theta band for PAC phase
theta_bands = np.array([[4, 8]])
x_theta = stx.dsp.filt.bandpass(xx, fs, theta_bands)
```

## FIR filter design utility

`stx.dsp.utils.filter.design_filter` exposes the underlying FIR design for inspection:

```python
from scitex.dsp.utils.filter import design_filter, plot_filter_responses

xx, tt, fs = stx.dsp.demo_sig()
seq_len = xx.shape[-1]

# Returns filter coefficients (numpy array)
bp_filter = design_filter(seq_len, fs, low_hz=30, high_hz=70)
lp_filter = design_filter(seq_len, fs, low_hz=30)
hp_filter = design_filter(seq_len, fs, high_hz=70)
bs_filter = design_filter(seq_len, fs, low_hz=30, high_hz=70, is_bandstop=True)

# Plot impulse + frequency response
fig = plot_filter_responses(bp_filter, fs, title="Bandpass 30-70 Hz")
```
