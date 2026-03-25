---
description: Built-in EEG frequency bands and standard electrode montages.
---

# stx.dsp.params — Parameters and Constants

Source: `/home/ywatanabe/proj/scitex-python/src/scitex/dsp/params.py`

## stx.dsp.params.BANDS

Standard EEG frequency bands as a pandas DataFrame.

```python
import scitex as stx

print(stx.dsp.params.BANDS)
#           delta  theta  lalpha  halpha   beta  gamma
# low_hz      0.5    4.0     8.0    10.0   13.0   32.0
# high_hz     4.0    8.0    10.0    13.0   32.0   75.0
```

### Access patterns

```python
bands = stx.dsp.params.BANDS

# Get a single band's range
delta_low  = bands["delta"]["low_hz"]   # 0.5
delta_high = bands["delta"]["high_hz"]  # 4.0

# Get as array for use with stx.dsp.filt.bandpass
import numpy as np

# All bands stacked
all_bands = bands.values.T  # shape (6, 2): [[low1, high1], ...]

# Single band
theta_band = np.array([[bands["theta"]["low_hz"], bands["theta"]["high_hz"]]])
# [[4.0, 8.0]]

# Multiple specific bands
gamma_beta = np.array([
    [bands["beta"]["low_hz"],  bands["beta"]["high_hz"]],
    [bands["gamma"]["low_hz"], bands["gamma"]["high_hz"]],
])
```

### Use with filtering

```python
import scitex as stx
import numpy as np

xx, tt, fs = stx.dsp.demo_sig(fs=256, t_sec=4)

bands = stx.dsp.params.BANDS

# Bandpass filter to theta (4-8 Hz)
theta_band = np.array([[bands["theta"]["low_hz"], bands["theta"]["high_hz"]]])
xx_theta = stx.dsp.filt.bandpass(xx, fs, theta_band)

# Filter to all standard bands at once
all_bands_array = bands.values.T  # (6, 2)
xx_all_bands = stx.dsp.filt.bandpass(xx, fs, all_bands_array)
# xx_all_bands.shape: (batch, chs, 6, time)
```

## stx.dsp.params.EEG_MONTAGE_1020

Standard 10-20 EEG electrode names (19 electrodes).

```python
stx.dsp.params.EEG_MONTAGE_1020
# ['FP1', 'F3', 'C3', 'P3', 'O1',
#  'FP2', 'F4', 'C4', 'P4', 'O2',
#  'F7', 'T7', 'P7', 'F8', 'T8', 'P8',
#  'FZ', 'CZ', 'PZ']
```

Used as default in `stx.dsp.get_eeg_pos()`.

## stx.dsp.params.EEG_MONTAGE_BIPOLAR_TRANVERSE

Bipolar transverse montage (14 channel pairs).

```python
stx.dsp.params.EEG_MONTAGE_BIPOLAR_TRANVERSE
# ['FP1-FP2', 'F7-F3', 'F3-FZ', 'FZ-F4', 'F4-F8',
#  'T7-C3', 'C3-CZ', 'CZ-C4', 'C4-T8',
#  'P7-P3', 'P3-PZ', 'PZ-P4', 'P4-P8',
#  'O1-O2']
```

## stx.dsp.get_eeg_pos (optional, requires MNE)

Get 3D electrode positions from the standard 10-20 montage.

```python
df = stx.dsp.get_eeg_pos(channel_names=stx.dsp.params.EEG_MONTAGE_1020)
# Returns DataFrame with columns = channel names, rows = [x, y, z]
```

Raises `ImportError` if `mne` is not installed.
