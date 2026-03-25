---
name: stx.dsp.wavelet
description: Continuous wavelet transform returning time-frequency phase and amplitude.
---

# stx.dsp.wavelet — Wavelet Transform

Source: `/home/ywatanabe/proj/scitex-python/src/scitex/dsp/_wavelet.py`

## Signature

```python
pha, amp, freqs = stx.dsp.wavelet(
    x,
    fs,
    freq_scale="linear",
    out_scale="linear",
    device="cuda",
    batch_size=32,
)
```

Computes a continuous wavelet transform (CWT) using the `Wavelet` module from `scitex.nn._Wavelet`. The function is decorated with both `@signal_fn` and `@batch_fn`, so it handles type conversion and automatic batch splitting when input is too large for GPU memory.

Requires `torch`.

### Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `x` | ndarray / Tensor | required | Signal, shape `(batch, chs, time)` |
| `fs` | float | required | Sampling frequency in Hz |
| `freq_scale` | str | `"linear"` | Frequency axis spacing: `"linear"` or `"log"` |
| `out_scale` | str | `"linear"` | Output amplitude scale: `"linear"` or `"log"` |
| `device` | str | `"cuda"` | PyTorch device |
| `batch_size` | int | `32` | Batch size for the `@batch_fn` wrapper |

### Returns

- `pha`: instantaneous phase, shape `(batch, chs, n_freqs, time)`
- `amp`: amplitude envelope, shape `(batch, chs, n_freqs, time)`
- `freqs`: frequency axis, shape `(batch, chs, n_freqs)` — take `freqs[0, 0]` for the 1D array

## Examples

```python
import scitex as stx
import numpy as np

xx, tt, fs = stx.dsp.demo_sig(
    sig_type="chirp", batch_size=4, n_chs=2, fs=512, t_sec=4
)

# Compute wavelet transform
pha, amp, freqs = stx.dsp.wavelet(xx, fs, device="cuda")

# freqs is per-batch/channel; take the 1D version
freqs_1d = freqs[0, 0]  # shape: (n_freqs,)

print(f"pha shape:  {pha.shape}")   # (4, 2, n_freqs, 2048)
print(f"amp shape:  {amp.shape}")   # (4, 2, n_freqs, 2048)
print(f"freqs: {freqs_1d}")
```

### Log-scale amplitude output

```python
pha, amp_log, freqs = stx.dsp.wavelet(xx, fs, out_scale="log")
# amp_log contains log(amplitude + 1e-5) — NaN-safe log scaling
```

### Spectrogram plot

```python
import matplotlib.pyplot as plt

pha, amp, freqs = stx.dsp.wavelet(xx, fs)
freqs_1d = freqs[0, 0].cpu().numpy()
i_batch, i_ch = 0, 0

fig, axes = plt.subplots(3, 1, figsize=(10, 8))

# Raw signal
axes[0].plot(tt, xx[i_batch, i_ch])
axes[0].set_ylabel("Amplitude")
axes[0].set_title("Signal")

# Amplitude spectrogram
log_amp = (amp[i_batch, i_ch] + 1e-5).log().cpu().numpy()
axes[1].imshow(log_amp.T, aspect="auto", origin="lower")
axes[1].set_ylabel("Frequency [Hz]")
axes[1].set_title("Wavelet Amplitude")

# Phase spectrogram
phase_np = pha[i_batch, i_ch].cpu().numpy()
axes[2].imshow(phase_np.T, aspect="auto", origin="lower")
axes[2].set_ylabel("Frequency [Hz]")
axes[2].set_title("Wavelet Phase [rad]")
axes[2].set_xlabel("Time [s]")
```

### Log frequency scale

```python
pha, amp, freqs = stx.dsp.wavelet(xx, fs, freq_scale="log")
# freqs are logarithmically spaced — more resolution at low frequencies
```

## PAC segments

When input has a segment dimension `(batch, chs, n_segments, time)`, extract one segment first:

```python
xx, tt, fs = stx.dsp.demo_sig(sig_type="pac", n_segments=20, fs=512, t_sec=4)
# xx.shape: (8, 19, 20, 2048) — has segment dim

i_segment = 0
xx_seg = xx[:, :, i_segment, :]  # (8, 19, 2048)
pha, amp, freqs = stx.dsp.wavelet(xx_seg, fs)
```
