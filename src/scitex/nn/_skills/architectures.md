---
name: stx.nn - Model Architectures
description: Complete neural network architectures for biosignal classification — ResNet1D, MNet1000, BNet (v1 and Residual). Designed for multi-channel EEG/MEG/LFP data shaped (batch, n_chs, seq_len).
---

# stx.nn — Model Architectures

---

## ResNet1D

1-D residual convolutional network. Suitable as a general-purpose signal classifier backbone.

```python
import torch
import scitex as stx

model = stx.nn.ResNet1D(
    n_chs=19,    # input channels
    n_out=10,    # output classes (reserved for FC head — currently not built in)
    n_blks=5,    # number of ResNetBasicBlock residual blocks
)

x = torch.randn(16, 19, 1024)   # (batch, n_chs, seq_len)
y = model(x)                     # (batch, n_chs * 4, seq_len)  — feature map, no FC head
```

### Notes
- Each block increases channels: block 0 maps `n_chs → n_chs * 4`; subsequent blocks keep `n_chs * 4`.
- The FC classification head is commented out in the current source; `forward()` returns the feature map.
- Use `ResNetBasicBlock` directly if you need a single residual stage inside another model.

---

## ResNetBasicBlock

A single residual block with three convolutions (k=7, k=5, k=3) and a channel-expansion shortcut.

```python
block = stx.nn.ResNetBasicBlock(
    in_chs=19,   # input channels
    out_chs=76,  # output channels (commonly 4× in_chs)
)

x = torch.randn(16, 19, 1024)
y = block(x)  # (16, 76, 1024)  — spatial dim preserved via padding
```

Each block: Conv(k=7) → BN → ReLU → Conv(k=5) → BN → ReLU → Conv(k=3) → BN → (+shortcut) → BN → ReLU.
Shortcut uses Conv(k=1) when `in_chs != out_chs`.

---

## MNet1000 / MNet_1000

A 2-D convolutional network originally designed for 270-channel signals at 1000 Hz.
`MNet_1000` is a deprecated alias for backward compatibility.

```python
MNet_config = {
    "classes": ["wake", "nrem", "rem"],   # class labels (len = n_output_classes)
    "n_chs": 270,                          # number of input channels
    "n_fc1": 1024,                         # FC hidden size 1
    "d_ratio1": 0.85,                      # dropout probability after FC1
    "n_fc2": 256,                          # FC hidden size 2
    "d_ratio2": 0.85,                      # dropout probability after FC2
}

model = stx.nn.MNet1000(config=MNet_config)

x = torch.randn(16, 270, 1000)
y = model(x)   # (16, n_classes)  logits
```

### Two-stage forward
```python
features = model.forward_bb(x)   # backbone only — returns (batch, n_fc1) features
logits   = model.fc(features)    # apply classification head
```

### Utility layers (also exported)
```python
# SwapLayer — transposes axes 1 and 2
swap = stx.nn.SwapLayer()
y = swap(x)   # x.transpose(1, 2)

# ReshapeLayer — flattens all dims except batch
reshape = stx.nn.ReshapeLayer()
y = reshape(x)   # x.reshape(len(x), -1)
```

---

## BNet_v1 (BNet from _BNet.py)

Multi-modal biosignal network. Accepts data from multiple recording modalities (e.g., MEG + EEG) with a shared backbone and per-modality heads.

```python
BNet_config = {
    "n_bands": 6,
    "SAMP_RATE": 250,
    "n_chs": [160, 19],      # channels per modality
    "n_classes": [2, 4],      # output classes per modality
    "n_fc1": 1024,
    "d_ratio1": 0.85,
    "n_fc2": 256,
    "d_ratio2": 0.85,
}

model = stx.nn.BNet_v1(
    BNet_config=BNet_config,
    MNet_config=stx.nn.MNet_config,   # MNet_config from _MNet_1000.py
)

x_meg = torch.randn(16, 160, 1000)
y_meg = model(x_meg, i_head=0)   # use modality 0 (MEG)

x_eeg = torch.randn(16, 19, 1000)
y_eeg = model(x_eeg, i_head=1)   # use modality 1 (EEG)
```

### Forward pipeline
```
z-score → DropoutChannels → FreqGainChanger
→ ChannelGainChanger[i_head] → BHead[i_head] (SpatialAttention + Conv1x1)
→ MNet1000 backbone (forward_bb) → FC head[i_head] → logits
```

**Warning:** The current `_BNet.py` source contains a debug `ipdb.set_trace()` call in `forward()`.

---

## BNet_Res (BNet from _BNet_Res.py)

Variant that replaces the MNet1000 backbone with `ResNetBasicBlock` blocks and average-pooling stages.

```python
BNet_config = {
    "n_bands": 6,
    "n_virtual_chs": 16,
    "SAMP_RATE": 250,
    "n_chs_of_modalities": [160, 19],
    "n_classes_of_modalities": [2, 4],
    "n_fc1": 1024,
    "d_ratio1": 0.85,
    "n_fc2": 256,
    "d_ratio2": 0.85,
}

model = stx.nn.BNet_Res(BNet_config=BNet_config, MNet_config=stx.nn.MNet_config)
y = model(x_meg, i_head=0)
```

### Backbone structure (after per-modality head)
```
BHead → blk1 → AvgPool → blk2 → AvgPool → blk3 → AvgPool → blk4 → AvgPool
      → blk5 → AvgPool → blk6 → AvgPool → blk7 → AvgPool
```
Each `blkN` is a `ResNetBasicBlock`. Channel counts halve every two blocks.

**Warning:** The current `_BNet_Res.py` source also contains a debug `ipdb.set_trace()` call.

---

## Default config objects

```python
# MNet default config (n_chs=270)
stx.nn.MNet_config   # dict from _MNet_1000.py

# BNet v1 default config
stx.nn.BNet_config_v1    # dict from _BNet.py

# BNet Res default config
stx.nn.BNet_config_Res   # dict from _BNet_Res.py
```
