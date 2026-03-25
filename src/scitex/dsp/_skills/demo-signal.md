---
description: Generate synthetic signals for testing — periodic, chirp, ripple, Gaussian, PAC, MEG.
---

# stx.dsp.demo_sig — Demo Signal Generation

Source: `/home/ywatanabe/proj/scitex-python/src/scitex/dsp/_demo_sig.py`

## Signature

```python
xx, tt, fs = stx.dsp.demo_sig(
    sig_type="periodic",
    batch_size=8,
    n_chs=19,
    n_segments=20,
    t_sec=4,
    fs=512,
    freqs_hz=None,
    verbose=False,
)
```

### Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `sig_type` | str | `"periodic"` | Signal type (see table below) |
| `batch_size` | int | `8` | Number of batches |
| `n_chs` | int | `19` | Number of channels |
| `n_segments` | int | `20` | Segments (only for `"tensorpac"` and `"pac"`) |
| `t_sec` | float | `4` | Duration in seconds |
| `fs` | int | `512` | Sampling frequency in Hz |
| `freqs_hz` | list or None | `None` | Frequencies for periodic signal; random if `None` |
| `verbose` | bool | `False` | Print frequency information |

### Returns

- `xx`: signal array, shape depends on `sig_type` (see table)
- `tt`: time vector, shape `(t_sec * fs,)`
- `fs`: sampling frequency (same as input)

## Signal types

| `sig_type` | Output shape | Requires | Description |
|------------|-------------|----------|-------------|
| `"uniform"` | `(batch, chs, time)` | — | Uniform random in `[-0.5, 0.5]` |
| `"gauss"` | `(batch, chs, time)` | — | Standard Gaussian noise |
| `"periodic"` | `(batch, chs, time)` | — | Sum of sine waves at `freqs_hz` |
| `"chirp"` | `(batch, chs, time)` | — | Linear frequency sweep with AM envelope |
| `"ripple"` | `(batch, chs, time)` | `ripple_detection` | Simulated hippocampal LFP with ripples |
| `"meg"` | `(batch, chs, time)` | `mne` | Real MEG segment from MNE sample dataset |
| `"tensorpac"` | `(batch, chs, segs, time)` | `tensorpac` | PAC signal via `pac_signals_wavelet` |
| `"pac"` | `(batch, chs, segs, time)` | — | Synthetic PAC: theta phase modulating gamma amplitude |

## Examples

```python
import scitex as stx

# Default: 8 batches, 19 channels, 4s at 512 Hz
xx, tt, fs = stx.dsp.demo_sig()
print(xx.shape)  # (8, 19, 2048)

# Chirp (frequency sweep)
xx, tt, fs = stx.dsp.demo_sig(sig_type="chirp", fs=512, t_sec=2)

# Periodic with specific frequencies
xx, tt, fs = stx.dsp.demo_sig(
    sig_type="periodic",
    freqs_hz=[10, 30, 100, 300],
    fs=1024,
    t_sec=1,
    batch_size=4,
    n_chs=2,
)

# PAC signal with segment dimension (for modulation_index)
xx, tt, fs = stx.dsp.demo_sig(sig_type="pac", n_segments=20, fs=512, t_sec=4)
print(xx.shape)  # (8, 19, 20, 2048)

# PAC signal using tensorpac wavelet method
xx, tt, fs = stx.dsp.demo_sig(sig_type="tensorpac", n_segments=20)

# Ripple simulation
xx, tt, fs = stx.dsp.demo_sig(sig_type="ripple", fs=1000, t_sec=10)
```

## Internal signal constructors

These private functions can be called directly for 1D signals:

```python
from scitex.dsp._demo_sig import (
    _demo_sig_periodic_1d,
    _demo_sig_chirp_1d,
    _demo_sig_ripple_1d,
)

# Single channel periodic
sig_1d = _demo_sig_periodic_1d(t_sec=2, fs=512, freqs_hz=[10, 40])

# Single channel chirp
sig_chirp = _demo_sig_chirp_1d(t_sec=2, fs=512, low_hz=5, high_hz=200)
```
