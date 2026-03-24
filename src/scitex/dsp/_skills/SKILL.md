---
name: stx.dsp
description: Digital signal processing for neuroscience: filtering, PSD, PAC, ripple detection, wavelets, and resampling.
---

# stx.dsp

The `stx.dsp` module provides digital signal processing (DSP) utilities tailored for neuroscience and time-series analysis. It covers spectral analysis, filtering, phase-amplitude coupling, hippocampal ripple detection, and signal segmentation.

## Python API

```python
import scitex as stx

# Generate demo signal (shape: channels x time)
sig, t = stx.dsp.demo_sig(fs=1000, duration=2.0)

# Bandpass filter
filtered = stx.dsp.filt.bandpass(sig, fs=1000, low=8, high=30)

# Power spectral density
freqs, psd = stx.dsp.psd(sig, fs=1000)
band_powers = stx.dsp.band_powers(sig, fs=1000)

# Hilbert transform (analytic signal)
amplitude, phase = stx.dsp.hilbert(sig)

# Phase-amplitude coupling
mi = stx.dsp.pac(sig, fs=1000, phase_band=(4, 8), amp_band=(30, 80))
mi = stx.dsp.modulation_index(phase_sig, amp_sig)

# Ripple detection (hippocampal)
ripples = stx.dsp.detect_ripples(sig, fs=1000)

# Wavelet transform
coeffs = stx.dsp.wavelet(sig, fs=1000, freqs=[4, 8, 16, 32])

# Resampling
resampled = stx.dsp.resample(sig, orig_fs=1000, target_fs=256)

# Segment into overlapping windows
segments = stx.dsp.to_segments(sig, window=256, step=128)

# Time array
t = stx.dsp.time(n_samples=1000, fs=1000)
```

## Key Features

- Filtering submodule: `stx.dsp.filt` — bandpass, bandstop, lowpass, highpass
- `psd` / `band_powers` — spectral analysis with band power extraction
- `hilbert` — analytic signal (amplitude envelope and instantaneous phase)
- `pac` / `modulation_index` — phase-amplitude coupling metrics
- `detect_ripples` — hippocampal sharp-wave ripple detection
- `wavelet` — continuous wavelet transform
- `resample` — signal resampling with anti-aliasing
- `to_segments` / `to_sktime_df` — segmentation and format conversion
