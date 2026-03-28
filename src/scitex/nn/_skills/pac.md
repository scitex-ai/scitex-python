---
description: GPU-accelerated differentiable Phase-Amplitude Coupling (PAC) and Modulation Index layers for EEG/LFP analysis. Supports static and learnable filter banks, surrogate-based z-scoring.
---

# stx.nn — Phase-Amplitude Coupling (PAC)

PAC measures how the amplitude of high-frequency oscillations is modulated by the phase of low-frequency oscillations. The `PAC` module is the high-level interface; `ModulationIndex` is the underlying metric.

---

## PAC

```python
import torch
import scitex as stx

layer = stx.nn.PAC(
    seq_len=4096,      # samples per segment
    fs=512,            # sampling rate Hz
    pha_start_hz=2,    # phase band lower bound Hz
    pha_end_hz=20,     # phase band upper bound Hz
    pha_n_bands=50,    # number of phase frequency bands
    amp_start_hz=60,   # amplitude band lower bound Hz
    amp_end_hz=160,    # amplitude band upper bound Hz
    amp_n_bands=30,    # number of amplitude frequency bands
    n_perm=None,       # int or None — if int, z-score against n_perm surrogates
    trainable=False,   # if True, use DifferentiableBandPassFilter (learnable bands)
    in_place=True,
    fp16=False,        # half precision
    amp_prob=False,    # if True, return amplitude probability distribution instead of MI
)
```

### Input shape
```
x: (batch_size, n_chs, seq_len)                           # 3D
x: (batch_size, n_chs, n_segments, seq_len)               # 4D preferred
```
3D input is automatically unsqueezed to 4D (n_segments=1).

### Output shape
```python
pac = layer(x)
# amp_prob=False, n_perm=None:
#   pac.shape: (batch_size, n_chs, pha_n_bands, amp_n_bands)
#   dtype: float16

# amp_prob=True:
#   returns amplitude probability per phase bin
#   shape: (batch_size, n_chs, pha_n_bands, amp_n_bands, n_segments, n_bins=18)

# n_perm=N (int):
#   returns PAC z-scored against N cut-and-shift surrogates
#   same shape as n_perm=None case
```

### Accessing frequency axes
```python
layer.PHA_MIDS_HZ  # center frequencies for phase bands, shape (pha_n_bands,)
layer.AMP_MIDS_HZ  # center frequencies for amplitude bands, shape (amp_n_bands,)
```

### Trainable mode (learnable band centers)
```python
layer = stx.nn.PAC(seq_len=4096, fs=512, trainable=True)
# Uses DifferentiableBandPassFilter internally
# layer.PHA_MIDS_HZ and layer.AMP_MIDS_HZ are nn.Parameter objects
# Gradients flow back through the filter centers

pac = layer(x)
pac.sum().backward()  # works
```

### Pipeline internals
```
x
→ BandPassFilter (or DifferentiableBandPassFilter)
    output: (batch*n_chs, n_segs, n_pha+n_amp, seq_len)
→ Hilbert
    output: (batch, n_chs, n_segs, n_pha+n_amp, seq_len, 2)  — [phase, amp]
→ edge trimming (seq_len // 8 from each end)
→ ModulationIndex
    output: (batch, n_chs, n_pha, n_amp)
```

---

## ModulationIndex

The Tort et al. (2010) Modulation Index metric. Used directly when you already have phase and amplitude tensors.

```python
layer = stx.nn.ModulationIndex(
    n_bins=18,    # number of phase bins over [-pi, pi]
    fp16=False,
    amp_prob=False,  # if True, return amplitude probability per bin instead of MI
)

# Required shapes:
# pha: (batch_size, n_channels, n_freqs_pha, n_segments, seq_len)
# amp: (batch_size, n_channels, n_freqs_amp, n_segments, seq_len)

mi = layer(pha, amp)
# mi.shape: (batch_size, n_channels, n_freqs_pha, n_freqs_amp)
# Values are averaged across n_segments dimension
```

### Phase bin centers
```python
layer.pha_bin_centers  # numpy array, shape (n_bins,), values in [-pi, pi]
```

### Algorithm
1. Assign each time sample to one of `n_bins` phase bins.
2. Compute mean amplitude per bin: `amp_mean[bin] = mean(amp[pha in bin])`.
3. Normalize to probability distribution: `amp_prob = amp_mean / sum(amp_mean)`.
4. MI = `(log(n_bins) + sum(amp_prob * log(amp_prob))) / log(n_bins)`
   — i.e., 1 - normalised entropy, so MI = 0 for uniform, MI = 1 for perfectly concentrated.

---

## Band helper methods (PAC static methods)

```python
# Phase bands: center ± 25% of center frequency
bands_pha = stx.nn.PAC.calc_bands_pha(start_hz=2, end_hz=20, n_bands=50)
# shape: (50, 2)

# Amplitude bands: center ± 12.5% of center frequency
bands_amp = stx.nn.PAC.calc_bands_amp(start_hz=30, end_hz=160, n_bands=100)
# shape: (100, 2)
```
