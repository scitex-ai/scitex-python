---
name: stx.dsp.psd / stx.dsp.band_powers
description: Power spectral density and per-band average power for multi-channel signals.
---

# stx.dsp — Spectral Analysis

Source: `/home/ywatanabe/proj/scitex-python/src/scitex/dsp/_psd.py`

## psd

```python
psd_vals, freqs = stx.dsp.psd(x, fs, prob=False, dim=-1)
```

Computes the power spectral density using the PyTorch `PSD` module from `scitex.nn._PSD`.

### Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `x` | ndarray / Tensor | required | Input signal, shape `(batch, chs, time)` |
| `fs` | float | required | Sampling frequency in Hz |
| `prob` | bool | `False` | If `True`, normalize PSD to sum to 1 (probability distribution) |
| `dim` | int | `-1` | Time dimension |

### Returns

- `psd_vals`: power spectrum, shape `(batch, chs, n_freqs)`, log-scaled
- `freqs`: frequency axis array, shape `(n_freqs,)`, in Hz

Requires `torch`.

## band_powers

```python
avg_powers = stx.dsp.band_powers(self, psd)
```

Computes average power within specified frequency bands from an existing PSD.

Note: `band_powers` as exposed in `__init__.py` is a lower-level function that requires `self` (a PSD instance) and a pre-computed `psd` tensor. It is typically used internally or via the `PSD` class directly.

## Built-in Frequency Bands

Predefined bands are available in `stx.dsp.params.BANDS`:

```python
import scitex as stx

print(stx.dsp.params.BANDS)
#           delta  theta  lalpha  halpha   beta  gamma
# low_hz      0.5    4.0     8.0    10.0   13.0   32.0
# high_hz     4.0    8.0    10.0    13.0   32.0   75.0
```

## Examples

```python
import scitex as stx

xx, tt, fs = stx.dsp.demo_sig(sig_type="chirp", fs=512, t_sec=4)

# Compute PSD
psd_vals, freqs = stx.dsp.psd(xx, fs)
# psd_vals.shape: (8, 19, n_freqs)
# freqs.shape: (n_freqs,)

# Normalized PSD (sums to 1 per channel)
psd_prob, freqs = stx.dsp.psd(xx, fs, prob=True)

# Plot PSD for first batch/channel
import matplotlib.pyplot as plt
fig, ax = plt.subplots()
ax.plot(freqs, psd_vals[0, 0])
ax.set_xlabel("Frequency [Hz]")
ax.set_ylabel("log(Power [uV^2 / Hz])")
```

## Full pipeline example

```python
import scitex as stx
import numpy as np

xx, tt, fs = stx.dsp.demo_sig(fs=512, t_sec=2)

# Filter to gamma band first, then compute PSD
gamma = stx.dsp.filt.bandpass(xx, fs, np.array([[32, 75]]))
psd_gamma, freqs = stx.dsp.psd(gamma, fs)

# Check which frequency has peak power in first batch/channel
peak_idx = psd_gamma[0, 0].argmax()
print(f"Peak frequency: {freqs[peak_idx]:.1f} Hz")
```
