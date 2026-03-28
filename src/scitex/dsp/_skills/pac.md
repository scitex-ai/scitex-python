---
description: Phase-amplitude coupling (PAC) via GPU-accelerated bandpass filtering and modulation index.
---

# stx.dsp — Phase-Amplitude Coupling

Sources:
- `/home/ywatanabe/proj/scitex-python/src/scitex/dsp/_pac.py`
- `/home/ywatanabe/proj/scitex-python/src/scitex/dsp/_modulation_index.py`

Both functions require `torch`. `pac` additionally benefits from CUDA.

## stx.dsp.pac

High-level end-to-end PAC from raw signal.

```python
pac_vals, pha_mids_hz, amp_mids_hz = stx.dsp.pac(
    x,
    fs,
    pha_start_hz=2,
    pha_end_hz=20,
    pha_n_bands=100,
    amp_start_hz=60,
    amp_end_hz=160,
    amp_n_bands=100,
    device="cuda",
    batch_size=1,
    batch_size_ch=-1,
    fp16=False,
    trainable=False,
    n_perm=None,
    amp_prob=False,
)
```

### Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `x` | ndarray / Tensor | required | Signal, shape `(batch, chs, time)` or `(batch, chs, segments, time)` |
| `fs` | float | required | Sampling frequency in Hz |
| `pha_start_hz` | float | `2` | Start of phase frequency range |
| `pha_end_hz` | float | `20` | End of phase frequency range |
| `pha_n_bands` | int | `100` | Number of phase bands to compute |
| `amp_start_hz` | float | `60` | Start of amplitude frequency range |
| `amp_end_hz` | float | `160` | End of amplitude frequency range |
| `amp_n_bands` | int | `100` | Number of amplitude bands to compute |
| `device` | str | `"cuda"` | PyTorch device, falls back to CPU if no GPU |
| `batch_size` | int | `1` | Batch size for processing |
| `batch_size_ch` | int | `-1` | Channel batch size; `-1` processes all at once |
| `fp16` | bool | `False` | Use half-precision for memory efficiency |
| `trainable` | bool | `False` | Make filter bank parameters learnable (gradient flows) |
| `n_perm` | int or None | `None` | Number of permutations for surrogate testing |
| `amp_prob` | bool | `False` | Normalize amplitude to probability distribution |

### Returns

- `pac_vals`: PAC values, shape `(batch, chs, pha_n_bands, amp_n_bands)`
- `pha_mids_hz`: center frequencies of phase bands, shape `(pha_n_bands,)`
- `amp_mids_hz`: center frequencies of amplitude bands, shape `(amp_n_bands,)`

## stx.dsp.modulation_index

Lower-level function: compute PAC from pre-computed phase and amplitude arrays.

```python
mi = stx.dsp.modulation_index(pha, amp, n_bins=18, amp_prob=False)
```

### Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `pha` | Tensor | required | Phase signal, shape `(batch, chs, n_freqs_pha, n_segments, seq_len)` |
| `amp` | Tensor | required | Amplitude signal, shape `(batch, chs, n_freqs_amp, n_segments, seq_len)` |
| `n_bins` | int | `18` | Number of phase bins for the mean-vector length computation |
| `amp_prob` | bool | `False` | Normalize amplitude distribution |

### Returns

- `mi`: modulation index values

## Helper: \_reshape

```python
reshaped = stx.dsp._reshape(x, batch_size=2, n_chs=4)
```

Utility to reshape a raw PAC tensor `x` into `(batch, chs, ...)` format for `modulation_index`.

## Examples

### End-to-end PAC

```python
import scitex as stx

FS = 512
xx, tt, fs = stx.dsp.demo_sig(
    batch_size=1, n_chs=1, fs=FS, t_sec=4, sig_type="tensorpac"
)

pac_vals, pha_mids, amp_mids = stx.dsp.pac(
    xx, fs,
    pha_start_hz=2, pha_end_hz=20, pha_n_bands=50,
    amp_start_hz=60, amp_end_hz=160, amp_n_bands=30,
)
# pac_vals.shape: (1, 1, 50, 30)

# Plot comodulogram
import matplotlib.pyplot as plt
fig, ax = plt.subplots()
im = ax.imshow(pac_vals[0, 0].T, origin="lower", aspect="auto")
ax.set_xlabel("Phase frequency [Hz]")
ax.set_ylabel("Amplitude frequency [Hz]")
plt.colorbar(im, label="PAC (MI)")
```

### Memory-efficient channel batching

```python
pac_vals, pha_mids, amp_mids = stx.dsp.pac(
    xx, fs,
    batch_size_ch=4,   # process 4 channels at a time
    fp16=True,         # halve memory usage
)
```

### Trainable filter banks (gradient-based optimization)

```python
# Filters become nn.Parameters; gradients flow through
pac_vals, pha_mids, amp_mids = stx.dsp.pac(
    xx, fs, trainable=True
)
pac_vals.sum().backward()  # gradients available on pha_mids / amp_mids
```

### Compare with Tensorpac

```python
from scitex.dsp.utils.pac import calc_pac_with_tensorpac, plot_pac_scitex_vs_tensorpac

# Tensorpac reference calculation
phases, amplitudes, freqs_pha, freqs_amp, pac_tp = calc_pac_with_tensorpac(
    xx, fs, t_sec=4, i_batch=0, i_ch=0
)

# Plot side-by-side comparison
fig = plot_pac_scitex_vs_tensorpac(
    pac_vals[0, 0], pac_tp, freqs_pha, freqs_amp
)
```
