---
description: Differentiable spectral analysis layers — Hilbert transform, Spectrogram (STFT), PSD, and Morlet Wavelet transform. All are nn.Module subclasses usable inside training loops.
---

# stx.nn — Spectral Analysis Layers

---

## Hilbert

Computes the analytic signal via the Hilbert transform and returns instantaneous **phase** and **amplitude** as the last dimension.

```python
import torch
import scitex as stx

seq_len = 1024
layer = stx.nn.Hilbert(
    seq_len=seq_len,
    dim=-1,        # dimension along which to apply FFT (default -1)
    fp16=False,    # use half precision
    in_place=False # if True, skips cloning the input
)

x = torch.randn(8, 19, seq_len)
out = layer(x)
# out.shape: (8, 19, seq_len, 2)
#   out[..., 0]  — instantaneous phase  (radians, range -pi to pi)
#   out[..., 1]  — instantaneous amplitude (envelope)
```

### Implementation details
- Uses `torch.fft.fft` / `torch.fft.ifft` for differentiability.
- Step function is approximated with `sigmoid(steepness=50 * freq)` to preserve gradients.
- Frequency buffer `f` is registered at init time (no re-allocation during forward).
- Output is always cast to float32 even when `fp16=True`.

---

## PSD

Differentiable Power Spectral Density via FFT.

```python
layer = stx.nn.PSD(
    sample_rate=256,  # Hz
    prob=False,       # if True, normalises PSD to sum=1 (treat as probability)
    dim=-1,           # dimension of the time axis
)

x = torch.randn(8, 19, 1024)
psd, freqs = layer(x)
# psd.shape:   same as x with the time dimension replaced by n_freq_bins
# freqs.shape: (n_freq_bins,)  — frequencies in Hz

# Complex input uses torch.fft.fft; real input uses torch.fft.rfft
```

### Notes
- Normalisation: `psd = |FFT(x)|^2 / seq_len / sample_rate`
- `prob=True` divides by `psd.sum(dim)` so bins sum to 1.

---

## Spectrogram

STFT-based spectrogram over multi-channel signals.

```python
layer = stx.nn.Spectrogram(
    sampling_rate=256,     # Hz
    n_fft=256,             # FFT size
    hop_length=None,       # default n_fft // 4
    win_length=None,       # default n_fft
    window="hann",         # only "hann" is supported
)

x = torch.randn(8, 19, 4096)      # (batch, n_chs, seq_len)
specs, freqs, times_sec = layer(x)
# specs.shape: (batch, n_chs, n_fft//2 + 1, n_frames)  — magnitude spectrogram
# freqs.shape: (n_fft//2 + 1,)  — Hz
# times_sec.shape: (n_frames,)  — seconds
```

### Convenience function
```python
from scitex.nn._Spectrogram import spectrograms

specs, freqs, times_sec = spectrograms(x, fs=256, cuda=True)
# Wraps Spectrogram(fs) in a @torch_fn decorator — accepts numpy or torch input
```

---

## Wavelet

Morlet continuous wavelet transform up to the Nyquist frequency.
Returns phase, log-amplitude (or amplitude), and frequency axes.

```python
layer = stx.nn.Wavelet(
    samp_rate=256,
    kernel_size=None,   # default = samp_rate samples
    freq_scale="linear", # "linear" or "log" — how frequency bins are spaced
    out_scale="log",     # "log" applies log(amp + 1e-5); anything else returns raw amp
)

x = torch.randn(8, 19, 4096)  # (batch, n_chs, seq_len)
pha, amp, freqs = layer(x)
# pha.shape:   (batch, n_chs, n_freqs, seq_len)  — instantaneous phase (radians)
# amp.shape:   (batch, n_chs, n_freqs, seq_len)  — log-amplitude or raw amplitude
# freqs.shape: (batch, n_chs, n_freqs)           — center frequency per filter (Hz)
```

### Frequency spacing
| `freq_scale` | Number of filters | Spacing |
|---|---|---|
| `"linear"` | `int(nyquist)` | 1 Hz steps up to Nyquist |
| `"log"` | `floor(log2(nyquist))` | Powers of 2 up to Nyquist |

### Implementation
- Kernels are complex Morlet wavelets (`sigma = 7 / (2π * center_freq)`).
- Real and imaginary parts convolved separately, then combined via `torch.view_as_complex`.
- Edge-reflection padding by `radius = kernel_size // 2` samples.

---

## Utility functions (from _Spectrogram.py)

```python
from scitex.nn._Spectrogram import my_softmax, unbias, normalize

# my_softmax — softmax along a dimension
y = my_softmax(x, dim=-1)          # @torch_fn decorated

# unbias — subtract min or mean along a dimension
y = unbias(x, func="min", dim=-1)  # func: "min" or "mean"
y = unbias(x, func="mean", dim=-1, cuda=True)

# normalize — scale by max absolute value
y = normalize(x, axis=-1, amp=1.0)
```
