---
name: stx.dsp.detect_ripples
description: Detect hippocampal sharp-wave ripples from wide-band LFP or EEG signals.
---

# stx.dsp.detect_ripples — Ripple Detection

Source: `/home/ywatanabe/proj/scitex-python/src/scitex/dsp/_detect_ripples.py`

## Signature

```python
df = stx.dsp.detect_ripples(
    xx,
    fs,
    low_hz,
    high_hz,
    sd=2.0,
    smoothing_sigma_ms=4,
    min_duration_ms=10,
    return_preprocessed_signal=False,
)
```

### Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `xx` | ndarray | required | Signal, shape `(n_chs, time)` or `(batch, n_chs, time)` |
| `fs` | float | required | Sampling frequency in Hz |
| `low_hz` | float | required | Lower edge of ripple band (e.g. `80`) |
| `high_hz` | float | required | Upper edge of ripple band (e.g. `140`) |
| `sd` | float | `2.0` | Threshold in standard deviations above mean for peak detection |
| `smoothing_sigma_ms` | float | `4` | Gaussian smoothing width in milliseconds |
| `min_duration_ms` | float | `10` | Minimum ripple duration in milliseconds |
| `return_preprocessed_signal` | bool | `False` | Also return the preprocessed RMS envelope |

### Returns

- If `return_preprocessed_signal=False` (default): pandas `DataFrame`
- If `return_preprocessed_signal=True`: `(df, xx_r, fs_r)` where `xx_r` is the preprocessed signal and `fs_r` is the downsampled fs

## Output DataFrame Columns

| Column | Type | Description |
|--------|------|-------------|
| `start_s` | float | Event start time in seconds |
| `end_s` | float | Event end time in seconds |
| `duration_s` | float | Event duration in seconds |
| `peak_s` | float | Time of peak amplitude in seconds |
| `rel_peak_pos` | float | Peak position within event, 0.0–1.0 |
| `peak_amp_sd` | float | Peak amplitude in standard deviations |

The DataFrame index holds the channel index for each detected event.

## Preprocessing pipeline (internal)

1. **Downsample** to `low_hz * 3` Hz to speed up computation
2. **Common-average subtraction** across channels to reduce EMG artifacts
3. **Bandpass filter** to `[low_hz, high_hz]`
4. **RMS envelope**: square, Hilbert amplitude, Gaussian smooth, square-root
5. **Average across channels**, then **z-score** normalization
6. **Peak detection** at threshold `sd` standard deviations
7. **Edge removal**: drop events within `3 / low_hz` seconds of recording edges

## Examples

```python
import scitex as stx

# Generate synthetic ripple signal (requires ripple_detection package)
xx, tt, fs = stx.dsp.demo_sig(sig_type="ripple", fs=1000, t_sec=10)

# Detect ripples in 80-140 Hz band
df = stx.dsp.detect_ripples(xx, fs, low_hz=80, high_hz=140)
print(df)
#    start_s  end_s  duration_s  peak_s  rel_peak_pos  peak_amp_sd

# Custom threshold: require 3 SD and 20 ms minimum duration
df = stx.dsp.detect_ripples(
    xx, fs,
    low_hz=80, high_hz=140,
    sd=3.0,
    min_duration_ms=20,
)

# Get preprocessed envelope for inspection
df, xx_r, fs_r = stx.dsp.detect_ripples(
    xx, fs,
    low_hz=80, high_hz=140,
    return_preprocessed_signal=True,
)
print(f"Preprocessed fs: {fs_r} Hz, shape: {xx_r.shape}")
```

## Low-level helper functions

These are exported from `stx.dsp` for advanced use:

```python
# Preprocessing (bandpass, RMS, z-score)
xx_r, fs_r = stx.dsp._preprocess(xx, fs, low_hz=80, high_hz=140)

# Event detection from preprocessed signal
df = stx.dsp._find_events(xx_r, fs_r, sd=2.0, min_duration_ms=10)

# Drop detections near recording edges
df = stx.dsp._drop_ripples_at_edges(df, low_hz=80, xx_r=xx_r, fs_r=fs_r)

# Add relative peak position column
df = stx.dsp._calc_relative_peak_position(df)

# Reorder columns into canonical order
df = stx.dsp._sort_columns(df)
```

## Typical ripple band parameters

| Region | Low Hz | High Hz |
|--------|--------|---------|
| Hippocampus SWR | 80 | 140 |
| Fast ripples | 200 | 400 |
| Sleep spindles | 12 | 15 |
