---
name: stx.dsp
description: Digital signal processing for neuroscience — filtering, spectral analysis, phase-amplitude coupling, ripple detection, wavelets, and resampling.
---

# stx.dsp — Skill Index

Digital signal processing (DSP) utilities for neuroscience and time-series analysis. All major functions accept NumPy arrays, PyTorch tensors, or pandas DataFrames via the `@signal_fn` decorator and return the same type as input.

## Sub-skills

| File | Feature Area |
|------|-------------|
| [filtering.md](filtering.md) | Bandpass, bandstop, lowpass, highpass, Gaussian filters |
| [spectral.md](spectral.md) | Power spectral density and band power extraction |
| [hilbert.md](hilbert.md) | Analytic signal: amplitude envelope and instantaneous phase |
| [pac.md](pac.md) | Phase-amplitude coupling (`pac`, `modulation_index`) |
| [ripple-detection.md](ripple-detection.md) | Hippocampal sharp-wave ripple detection |
| [wavelet.md](wavelet.md) | Continuous wavelet transform |
| [resampling.md](resampling.md) | Anti-aliased up/down resampling |
| [segmentation.md](segmentation.md) | Sliding-window segmentation and sktime conversion |
| [noise.md](noise.md) | Add Gaussian, white, pink, or brown noise |
| [normalization.md](normalization.md) | Z-score and min-max normalization |
| [referencing.md](referencing.md) | Common-average, random, and target re-referencing |
| [demo-signal.md](demo-signal.md) | Synthetic signal generation for testing |
| [params.md](params.md) | Built-in EEG frequency bands and electrode montages |
| [utils.md](utils.md) | Helpers: zero-padding, FIR filter design, differentiable bandpass filters |

## Quick Start

```python
import scitex as stx
import numpy as np

# Generate demo signal: shape (batch=8, chs=19, time=2048)
xx, tt, fs = stx.dsp.demo_sig(sig_type="chirp", fs=512, t_sec=4)

# Bandpass filter 8-30 Hz
xx_bp = stx.dsp.filt.bandpass(xx, fs, np.array([[8, 30]]))

# Power spectral density
psd_vals, freqs = stx.dsp.psd(xx, fs)

# Wavelet transform -> phase, amplitude, frequency axis
pha, amp, freqs_w = stx.dsp.wavelet(xx, fs)
```

## Optional Dependencies

| Feature | Requires | Install |
|---------|----------|---------|
| Filters, PSD, PAC, wavelet, resample | `torch`, `torchaudio` | `pip install torch torchaudio` |
| Audio device listing | `sounddevice`, PortAudio | `pip install sounddevice` + `apt install portaudio19-dev` |
| EEG electrode positions | `mne` | `pip install mne` |
| Ripple demo signal | `ripple_detection` | `pip install ripple_detection` |
| Tensorpac demo / PAC comparison | `tensorpac` | `pip install tensorpac` |
