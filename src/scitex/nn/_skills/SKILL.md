---
name: stx.nn
description: Neural network layers and modules for neuroscience signal processing (EEG, LFP, spectrogram, PAC). All layers are nn.Module subclasses that work inside standard PyTorch training pipelines.
---

# stx.nn

The `stx.nn` module provides PyTorch `nn.Module` layers specialized for neuroscience signal processing.  All layers accept 3-D tensors shaped `(batch_size, n_chs, seq_len)` unless noted, and are differentiable by default.

## Sub-skills

| File | Feature area |
|---|---|
| [filters.md](filters.md) | FIR filter layers: BandPassFilter, BandStopFilter, LowPassFilter, HighPassFilter, GaussianFilter, DifferentiableBandPassFilter, BaseFilter1D |
| [spectral.md](spectral.md) | Spectral analysis: Hilbert, PSD, Spectrogram, Wavelet |
| [pac.md](pac.md) | Phase-Amplitude Coupling: PAC, ModulationIndex |
| [architectures.md](architectures.md) | Complete models: ResNet1D, MNet1000, BNet_v1, BNet_Res |
| [augmentation.md](augmentation.md) | Training augmentation: DropoutChannels, SwapChannels, ChannelGainChanger, FreqGainChanger, AxiswiseDropout |
| [utility-layers.md](utility-layers.md) | Building blocks: SpatialAttention, TransposeLayer, GaussianFilter (radius-based), SwapLayer, ReshapeLayer |

## Quick orientation

```python
import scitex as stx
import torch
import numpy as np

x = torch.randn(8, 19, 1024)   # batch=8, channels=19, time=1024

# --- Filters ---
bands = np.array([[4.0, 8.0], [8.0, 13.0]])
y = stx.nn.BandPassFilter(bands=bands, fs=256, seq_len=1024)(x)
# output: (8, 19, 2, 1024)  — one output band per filter

# --- Spectral ---
pha, amp, freqs = stx.nn.Wavelet(samp_rate=256)(x)
psd, freqs = stx.nn.PSD(sample_rate=256)(x)
out = stx.nn.Hilbert(seq_len=1024)(x)   # (..., 2): [phase, amplitude]

# --- PAC ---
pac_layer = stx.nn.PAC(seq_len=1024, fs=256)
pac = pac_layer(x)   # (8, 19, n_pha_bands, n_amp_bands)

# --- Architectures ---
model = stx.nn.ResNet1D(n_chs=19, n_blks=5)
model = stx.nn.MNet1000(stx.nn.MNet_config)

# --- Augmentation (training only) ---
x = stx.nn.DropoutChannels(dropout=0.1)(x)
x = stx.nn.SwapChannels(dropout=0.5)(x)
x = stx.nn.ChannelGainChanger(n_chs=19)(x)

# --- Utility ---
x = stx.nn.SpatialAttention(n_chs_in=19)(x)
x = stx.nn.TransposeLayer(axis1=1, axis2=2)(x)
```

## Exported names

```python
# Filters
stx.nn.BaseFilter1D
stx.nn.BandPassFilter
stx.nn.BandStopFilter
stx.nn.LowPassFilter
stx.nn.HighPassFilter
stx.nn.GaussianFilter            # from _Filters.py (sigma-based)
stx.nn.DifferentiableBandPassFilter

# Spectral
stx.nn.Hilbert
stx.nn.PSD
stx.nn.Spectrogram
stx.nn.Wavelet
stx.nn.spectrograms              # function (torch_fn decorated)
stx.nn.my_softmax                # function
stx.nn.normalize                 # function
stx.nn.unbias                    # function

# PAC
stx.nn.PAC
stx.nn.ModulationIndex

# Architectures
stx.nn.ResNet1D
stx.nn.ResNetBasicBlock
stx.nn.MNet1000
stx.nn.MNet_1000                 # deprecated alias for MNet1000
stx.nn.MNet_config               # default config dict
stx.nn.BNet_v1                   # alias BNet from _BNet.py
stx.nn.BNet_Res                  # alias BNet from _BNet_Res.py
stx.nn.BNet_config_v1            # default config dict (_BNet.py)
stx.nn.BNet_config_Res           # default config dict (_BNet_Res.py)
stx.nn.BHead_v1                  # BHead from _BNet.py
stx.nn.BHead_Res                 # BHead from _BNet_Res.py
stx.nn.SwapLayer
stx.nn.ReshapeLayer

# Augmentation
stx.nn.AxiswiseDropout
stx.nn.DropoutChannels
stx.nn.SwapChannels
stx.nn.ChannelGainChanger
stx.nn.FreqGainChanger

# Utility
stx.nn.SpatialAttention
stx.nn.TransposeLayer
```
