---
name: stx.dsp.resample
description: Anti-aliased signal resampling using torchaudio.
---

# stx.dsp.resample — Resampling

Source: `/home/ywatanabe/proj/scitex-python/src/scitex/dsp/_resample.py`

## Signature

```python
xr = stx.dsp.resample(x, src_fs, tgt_fs, t=None)
# or, with time vector:
xr, tr = stx.dsp.resample(x, src_fs, tgt_fs, t=tt)
```

Uses `torchaudio.transforms.Resample` for polyphase anti-aliased resampling. Decorated with `@signal_fn`.

Requires `torch` and `torchaudio`.

### Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `x` | ndarray / Tensor | required | Signal, shape `(batch, chs, time)` |
| `src_fs` | float | required | Source sampling frequency in Hz |
| `tgt_fs` | float | required | Target sampling frequency in Hz |
| `t` | ndarray or None | `None` | Optional time vector; if given, a resampled time vector is also returned |

### Returns

- `xr`: resampled signal, shape `(batch, chs, new_time)` where `new_time = round(time * tgt_fs / src_fs)`
- If `t` is provided: `(xr, tr)` where `tr` is a new time vector spanning the same range as `t`

## Examples

```python
import scitex as stx

T_SEC = 1
SRC_FS = 128
xx, tt, fs = stx.dsp.demo_sig(sig_type="chirp", t_sec=T_SEC, fs=SRC_FS)

# Downsample to 64 Hz
xd, td = stx.dsp.resample(xx, fs, 64, t=tt)
print(f"Original: {xx.shape}, {tt.shape}")
print(f"Downsampled: {xd.shape}, {td.shape}")

# Upsample to 256 Hz
xu, tu = stx.dsp.resample(xx, fs, 256, t=tt)
print(f"Upsampled: {xu.shape}, {tu.shape}")

# Without time vector
xd = stx.dsp.resample(xx, fs, 64)
```

## Common use cases

```python
import scitex as stx
import numpy as np

xx, tt, fs = stx.dsp.demo_sig(fs=1000, t_sec=10)

# Preprocessing pipeline: downsample before filtering for speed
xx_256, tt_256 = stx.dsp.resample(xx, fs, 256, t=tt)
xx_filt = stx.dsp.filt.bandpass(xx_256, 256, np.array([[4, 80]]))

# Resample before ripple detection (detect_ripples does this internally)
# but you can pre-downsample manually:
xx_low = stx.dsp.resample(xx, fs, 300)  # ripple band is 80-140 Hz; 3x = 420 Hz

# Match sampling rates between two recordings
xx_a, tt_a, fs_a = stx.dsp.demo_sig(fs=1024)
xx_b, tt_b, fs_b = stx.dsp.demo_sig(fs=512)
xx_a_resampled = stx.dsp.resample(xx_a, fs_a, fs_b)
```

## Notes

- The resampled time vector `tr` is computed with `torch.linspace(t[0], t[-1], new_len)`, preserving the original time span.
- Resampling uses the dtype of the input tensor; convert to float32 first if needed.
- `detect_ripples` internally downsamples to `low_hz * 3` Hz automatically.
