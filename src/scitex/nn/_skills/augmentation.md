---
name: stx.nn - Data Augmentation Layers
description: Training-only augmentation layers for multi-channel biosignals — channel dropout, channel swapping, channel gain jitter, frequency band gain jitter, and axis-wise dropout.
---

# stx.nn — Data Augmentation Layers

All augmentation layers are **no-ops at eval time** (i.e., they return `x` unchanged when `model.eval()` is active).  They are `nn.Module` subclasses and integrate seamlessly into `nn.Sequential` pipelines.

Input convention: `(batch_size, n_chs, seq_len)` unless noted.

---

## DropoutChannels

Replaces a random subset of channels with Gaussian noise.

```python
import torch
import scitex as stx

layer = stx.nn.DropoutChannels(dropout=0.5)
# dropout: float — probability that any given channel is replaced with noise

layer.train()
x = torch.randn(16, 19, 1024)
y = layer(x)   # some channels replaced with torch.randn(...) noise

layer.eval()
y = layer(x)   # identical to x, no modification
```

Channels selected for replacement are identified by applying `nn.Dropout` to a ones-vector, then setting those channel slots to fresh standard-normal samples on the same device as `x`.

---

## SwapChannels

Randomly permutes a subset of channels during training.

```python
layer = stx.nn.SwapChannels(dropout=0.5)
# dropout: float — probability that any channel participates in swapping

layer.train()
y = layer(x)   # some channels shuffled among themselves
layer.eval()
y = layer(x)   # x unchanged
```

Channels not selected by the dropout mask keep their original positions; selected channels are randomly permuted among themselves using `random.sample`.

---

## ChannelGainChanger

Applies per-channel random gain during training.

```python
layer = stx.nn.ChannelGainChanger(n_chs=19)
# n_chs: int — must match x.shape[1]

layer.train()
y = layer(x)
# Each channel is multiplied by a gain in [0.5, 1.5] range,
# then softmax-normalised across channels so total power is preserved.

layer.eval()
y = layer(x)   # x unchanged
```

Gain vector: `rand(n_chs) + 0.5`, then `softmax(gains, dim=1)`.

---

## FreqGainChanger

Splits the signal into `n_bands` frequency sub-bands using Julius, applies a random gain per band, then sums them back.

```python
layer = stx.nn.FreqGainChanger(
    n_bands=6,
    samp_rate=250,
    dropout_ratio=0.5,   # parameter exists but not currently used in forward()
)

layer.train()
y = layer(x)
# Internally: julius.bands.split_bands → per-band random gains (softmax-normalised) → sum

layer.eval()
y = layer(x)   # x unchanged
```

**Dependency:** Requires the `julius` package (`pip install julius`).

---

## AxiswiseDropout

Drops entire slices along a specified axis at training time (structured dropout).

```python
layer = stx.nn.AxiswiseDropout(
    dropout_prob=0.5,   # probability of dropping a slice
    dim=1,              # axis to apply structured dropout on
)

layer.train()
x = torch.randn(8, 32, 1024)
y = layer(x)
# A binary mask of shape (8, 32, 1) is generated; zero-masked channels are zeroed
# across the entire time dimension (entire channel zeroed, not individual samples)

layer.eval()
y = layer(x)   # x unchanged
```

Use `dim=0` to drop entire batch examples, `dim=1` for channels, `dim=-1` for time steps.

---

## Summary table

| Layer | What it randomises | Preserves shape |
|---|---|---|
| `DropoutChannels` | Channel content (replaced with noise) | Yes |
| `SwapChannels` | Channel ordering | Yes |
| `ChannelGainChanger` | Per-channel amplitude scaling | Yes |
| `FreqGainChanger` | Per-frequency-band amplitude | Yes |
| `AxiswiseDropout` | Structured zeros along one axis | Yes |
