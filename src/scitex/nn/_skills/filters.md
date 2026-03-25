---
name: stx.nn - Filters
description: Fixed and differentiable FIR filter layers for 1D biosignal processing. Input shape is always (batch_size, n_chs, seq_len); output adds a filter dimension.
---

# stx.nn — Filters

All filter classes inherit from `BaseFilter1D(nn.Module)` and apply FIR convolution with edge-reflection padding to avoid boundary artifacts.

## Input / Output contract

```
input:  (batch_size, n_chs, seq_len)
output: (batch_size, n_chs, n_filters, seq_len)
```

`edge_len` can be passed to `forward()` to trim transient edges from the output.
Pass `edge_len="auto"` to trim `seq_len // 8` samples from each end.

---

## BandPassFilter

Keep only the energy within specified frequency bands.

```python
import numpy as np
import torch
import scitex as stx

bands = np.array([[4.0, 8.0], [8.0, 13.0], [13.0, 30.0]])  # (n_bands, 2) Hz
fs     = 256   # sampling rate Hz
seq_len = 1024

layer = stx.nn.BandPassFilter(bands=bands, fs=fs, seq_len=seq_len)
# bands: np.ndarray or torch.Tensor, shape (n_bands, 2) — [low_hz, high_hz] per row
# fs:      float — sampling rate in Hz
# seq_len: int   — expected input length (determines kernel length)
# fp16:    bool  — half precision (default False)

x = torch.randn(8, 19, seq_len)
y = layer(x)                     # (8, 19, 3, 1024)
y, t = layer(x, t=time_vector)   # also trims time vector if provided
```

### Constraints
- Each band must satisfy: `0 < low_hz < high_hz < fs/2`
- Bands are clipped to `[0.1, nyquist - 1]` automatically.

---

## BandStopFilter

Attenuate (notch) the energy within specified frequency bands.

```python
bands = np.array([[49.0, 51.0], [99.0, 101.0]])  # 50 Hz + 100 Hz notch
layer = stx.nn.BandStopFilter(bands=bands, fs=fs, seq_len=seq_len)
# Same signature as BandPassFilter except no fp16 argument
```

---

## LowPassFilter

Keep energy below cutoff frequencies.

```python
cutoffs_hz = np.array([30.0, 50.0])   # shape (n_cutoffs,) — one filter per cutoff
layer = stx.nn.LowPassFilter(cutoffs_hz=cutoffs_hz, fs=fs, seq_len=seq_len)

y = layer(x)  # (batch, n_chs, 2, seq_len)
```

---

## HighPassFilter

Keep energy above cutoff frequencies.

```python
cutoffs_hz = np.array([1.0, 4.0])
layer = stx.nn.HighPassFilter(cutoffs_hz=cutoffs_hz, fs=fs, seq_len=seq_len)
```

---

## GaussianFilter (from _Filters.py)

Gaussian smoothing along the time axis.  The kernel covers ± 3 standard deviations.

```python
layer = stx.nn.GaussianFilter(sigma=5)
# sigma: int — standard deviation in samples. kernel_size = sigma * 6.
# Note: there are TWO GaussianFilter classes in the module.
#   stx.nn.GaussianFilter   →  imported from _Filters.py (subclass of BaseFilter1D)
#   _GaussianFilter.GaussianFilter → separate class with radius-based constructor
```

The `_Filters.py` version:
- output shape: `(batch, n_chs, 1, seq_len)` — a single filter dimension
- kernel is normalized to sum = 1

---

## DifferentiableBandPassFilter

A learnable filter bank designed for Phase-Amplitude Coupling (PAC) pipelines.
Band center frequencies are `nn.Parameter`s that can be gradient-updated.

```python
layer = stx.nn.DifferentiableBandPassFilter(
    sig_len=1024,
    fs=256,
    pha_low_hz=2,     # lower bound for phase-band centers
    pha_high_hz=20,
    pha_n_bands=30,   # number of phase filters
    amp_low_hz=80,    # lower bound for amplitude-band centers
    amp_high_hz=160,
    amp_n_bands=50,   # number of amplitude filters
    cycle=3,          # number of cycles per wavelet kernel
    fp16=False,
)

# Learnable parameters (center frequencies):
print(layer.pha_mids)  # nn.Parameter, shape (pha_n_bands,)
print(layer.amp_mids)  # nn.Parameter, shape (amp_n_bands,)

y = layer(x)  # (batch, n_chs, pha_n_bands + amp_n_bands, seq_len)
y.sum().backward()  # gradients flow through to pha_mids / amp_mids
```

### Notes
- During `forward()`, `pha_mids` and `amp_mids` are clamped to their declared ranges.
- Used internally by `PAC(trainable=True)`.

---

## BaseFilter1D

Abstract base class.  Extend it to add a custom filter type:

```python
class MyFilter(stx.nn.BaseFilter1D):
    def __init__(self, ...):
        super().__init__(fp16=False)
        kernels = ...  # torch.Tensor shape (n_filters, kernel_len)
        self.register_buffer("kernels", kernels)

    def init_kernels(self):
        pass  # required by abstractmethod; logic can live in __init__

# forward() is inherited; applies flip-extend padding + batch_conv
```

Key static helpers available on every filter:
- `BaseFilter1D.flip_extend(x, extension_length)` — reflect-pad both ends
- `BaseFilter1D.batch_conv(x, kernels, padding)` — grouped 1-D convolution over batch × channels
- `BaseFilter1D.remove_edges(x, edge_len)` — trim edge artifacts
