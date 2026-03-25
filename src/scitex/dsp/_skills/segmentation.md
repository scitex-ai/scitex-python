---
name: stx.dsp.to_segments / stx.dsp.crop / stx.dsp.to_sktime_df
description: Sliding-window segmentation, signal cropping, and sktime DataFrame conversion.
---

# stx.dsp — Segmentation

Sources:
- `/home/ywatanabe/proj/scitex-python/src/scitex/dsp/_transform.py`
- `/home/ywatanabe/proj/scitex-python/src/scitex/dsp/_crop.py`

## stx.dsp.to_segments

PyTorch-based sliding-window segmentation using `unfold`.

```python
windows = stx.dsp.to_segments(x, window_size, overlap_factor=1, dim=-1)
```

Decorated with `@torch_fn`.

### Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `x` | Tensor / ndarray | required | Input signal |
| `window_size` | int | required | Number of samples per window |
| `overlap_factor` | int | `1` | Stride = `window_size // overlap_factor`; `1` = no overlap, `2` = 50% overlap |
| `dim` | int | `-1` | Time dimension to segment |

### Returns

Tensor with a new trailing dimension: `(..., n_windows, window_size)`.

### Example

```python
import scitex as stx

xx, tt, fs = stx.dsp.demo_sig()
# xx.shape: (8, 19, 2048)

# Non-overlapping 256-sample windows
segments = stx.dsp.to_segments(xx, window_size=256)
# segments.shape: (8, 19, n_windows, 256)

# 50% overlapping windows
segments_50 = stx.dsp.to_segments(xx, window_size=256, overlap_factor=2)
```

## stx.dsp.crop

NumPy-based signal cropping into windows. More flexible than `to_segments`: works on any axis and returns an optional time array.

```python
cropped = stx.dsp.crop(sig_2d, window_length, overlap_factor=0.0, axis=-1, time=None)
# or
cropped, cropped_times = stx.dsp.crop(sig_2d, window_length, overlap_factor=0.5, time=tt)
```

### Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `sig_2d` | ndarray | required | Signal array, any dimensionality |
| `window_length` | int | required | Window length in samples |
| `overlap_factor` | float | `0.0` | Fraction overlap between windows (0.0 = no overlap, 0.5 = 50%) |
| `axis` | int | `-1` | Axis to crop along |
| `time` | ndarray or None | `None` | Time vector matching length along `axis` |

### Returns

- `cropped_windows`: shape `(n_windows, *original_shape_with_window_axis)`
- If `time` is given: `(cropped_windows, cropped_times)` where `cropped_times.shape = (n_windows, window_length)`

### Example

```python
import scitex as stx
import numpy as np

FS = 128
sig2d = np.random.rand(19, FS * 13)   # 19 channels, 13 seconds
time  = np.arange(sig2d.shape[-1]) / FS

window_pts = FS * 2  # 2-second windows

# 50% overlapping crop
xx, tt = stx.dsp.crop(sig2d, window_pts, overlap_factor=0.5, time=time)
# xx.shape: (n_windows, 19, 256)
# tt.shape: (n_windows, 256)

# No time output
xx = stx.dsp.crop(sig2d, window_pts, overlap_factor=0.5)
```

## stx.dsp.to_sktime_df

Convert a 3D array to sktime-compatible DataFrame format (nested DataFrames).

```python
df = stx.dsp.to_sktime_df(arr)
```

### Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `arr` | ndarray | Shape `(n_samples, seq_len, n_channels)` — note axis order |

### Returns

pandas `DataFrame` with one column (`dim_0`), where each cell contains a `pd.Series` of all channels for that sample.

### Example

```python
import scitex as stx
import numpy as np

arr = np.random.randn(100, 256, 4)  # 100 samples, 256 timepoints, 4 channels
sktime_df = stx.dsp.to_sktime_df(arr)
# sktime_df.shape: (100, 1)
# sktime_df.iloc[0, 0]: Series with channel_0, channel_1, channel_2, channel_3
```

## Comparison: `crop` vs `to_segments`

| | `crop` | `to_segments` |
|-|--------|---------------|
| Backend | NumPy | PyTorch |
| Time vector | Supported | Not supported |
| Overlap spec | Float fraction (0.0–1.0) | Integer factor |
| Input dims | Any | `dim` parameter |
| Decorator | None | `@torch_fn` |
