---
description: Internal helpers — zero-padding, FIR filter design, differentiable bandpass filter banks.
---

# stx.dsp.utils — Utilities

Source directory: `/home/ywatanabe/proj/scitex-python/src/scitex/dsp/utils/`

These utilities are used internally by the higher-level DSP functions but can also be called directly.

## Zero-padding

Source: `utils/_zero_pad.py`

```python
from scitex.dsp.utils import zero_pad, _zero_pad_1d
```

### `_zero_pad_1d(x, target_length)`

Zero-pad a 1D tensor to a target length, padding symmetrically.

```python
from scitex.dsp.utils import _zero_pad_1d
import torch

x = torch.tensor([1.0, 2.0, 3.0])
padded = _zero_pad_1d(x, target_length=7)
# tensor([0., 1., 2., 3., 0., 0., 0.])  — 2 left, 2 right
```

### `zero_pad(xs, dim=0)`

Zero-pad a list of variable-length tensors/arrays to the same length and stack them.

```python
from scitex.dsp.utils import zero_pad
import torch

xs = [torch.tensor([1.0, 2.0]), torch.tensor([3.0, 4.0, 5.0])]
stacked = zero_pad(xs, dim=0)
# tensor([[1., 2., 0.],
#         [3., 4., 5.]])
```

Accepts NumPy arrays, converts them to tensors automatically.

## FIR filter design

Source: `utils/filter.py`

```python
from scitex.dsp.utils.filter import design_filter, plot_filter_responses
```

### `design_filter(sig_len, fs, low_hz=None, high_hz=None, cycle=3, is_bandstop=False)`

Design an FIR filter using `scipy.signal.firwin` with Hamming window. Returns filter coefficient array.

Decorated with `@numpy_fn` (converts tensors to arrays automatically).

| Parameter | Description |
|-----------|-------------|
| `sig_len` | Signal length (determines maximum filter order) |
| `fs` | Sampling frequency |
| `low_hz` | Low cutoff (omit for highpass) |
| `high_hz` | High cutoff (omit for lowpass) |
| `cycle` | Number of cycles at lowest frequency; determines filter order |
| `is_bandstop` | `True` for bandstop when both `low_hz` and `high_hz` given |

Filter type selection:
- `low_hz` only → lowpass
- `high_hz` only → highpass
- both → bandpass (default) or bandstop (`is_bandstop=True`)

```python
from scitex.dsp.utils.filter import design_filter, plot_filter_responses
import scitex as stx

xx, tt, fs = stx.dsp.demo_sig()
seq_len = xx.shape[-1]

bp = design_filter(seq_len, fs, low_hz=30, high_hz=70)
lp = design_filter(seq_len, fs, low_hz=30)
hp = design_filter(seq_len, fs, high_hz=70)
bs = design_filter(seq_len, fs, low_hz=30, high_hz=70, is_bandstop=True)
```

### `plot_filter_responses(filter, fs, worN=8000, title=None)`

Plot impulse response and frequency response of an FIR filter. Returns a matplotlib `Figure`.

```python
fig = plot_filter_responses(bp, fs, title="Bandpass 30-70 Hz")
```

## Differentiable bandpass filter banks (for gradient-based optimization)

Source: `utils/_differential_bandpass_filters.py`

```python
from scitex.dsp.utils import init_bandpass_filters, build_bandpass_filters
```

These build learnable PAC filter banks whose center frequencies can be optimized via backpropagation.

Requires `torchaudio.prototype.functional.sinc_impulse_response`.

### `init_bandpass_filters(sig_len, fs, pha_low_hz, pha_high_hz, pha_n_bands, amp_low_hz, amp_high_hz, amp_n_bands, cycle)`

Initialize a filter bank with learnable `pha_mids` and `amp_mids` parameters.

```python
from scitex.dsp.utils import init_bandpass_filters
import scitex as stx

xx, tt, fs = stx.dsp.demo_sig(fs=1024)
filters, pha_mids, amp_mids = init_bandpass_filters(
    sig_len=xx.shape[-1],
    fs=fs,
    pha_low_hz=2, pha_high_hz=20, pha_n_bands=30,
    amp_low_hz=60, amp_high_hz=160, amp_n_bands=50,
)
# filters: stacked impulse responses shape (pha_n_bands + amp_n_bands, filter_len)
# pha_mids, amp_mids: nn.Parameter — gradients flow through these

# Verify gradients work
filters.sum().backward()
print(pha_mids.grad)  # not None
```

### `build_bandpass_filters(sig_len, fs, pha_mids, amp_mids, cycle)`

Rebuild filter bank from (updated) center frequency parameters. Call this in the forward pass after optimizer.step() to apply learned frequencies.

```python
from scitex.dsp.utils import build_bandpass_filters

# After optimizer step:
new_filters = build_bandpass_filters(sig_len, fs, pha_mids, amp_mids, cycle=3)
```

## ensure_3d

Source: `utils/_ensure_3d.py` (also available as `stx.dsp.ensure_3d`)

```python
x_3d = stx.dsp.ensure_3d(x)
```

Promotes 1D `(time,)` or 2D `(batch, time)` tensors to 3D `(batch, chs, time)` for compatibility with all DSP functions.

```python
import torch
import scitex as stx

x1d = torch.randn(512)
x2d = torch.randn(8, 512)
x3d = torch.randn(8, 19, 512)

stx.dsp.ensure_3d(x1d).shape  # (1, 1, 512)
stx.dsp.ensure_3d(x2d).shape  # (8, 1, 512)
stx.dsp.ensure_3d(x3d).shape  # (8, 19, 512) — unchanged
```

## stx.dsp.time

Source: `/home/ywatanabe/proj/scitex-python/src/scitex/dsp/_time.py`

Generate a time vector using `stx.gen.float_linspace`.

```python
t = stx.dsp.time(start_sec=0, end_sec=5, fs=256)
# Returns array of (end_sec - start_sec) * fs evenly spaced values
```
