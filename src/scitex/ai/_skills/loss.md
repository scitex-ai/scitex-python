---
description: Loss function utilities — MultiTaskLoss for automatic uncertainty-weighted multi-task learning, plus L1/L2/elastic regularization helpers.
---

# Loss Functions

## MultiTaskLoss

Implements uncertainty-based automatic task weighting for multi-task learning.

Based on: Kendall et al., "Multi-Task Learning Using Uncertainty to Weigh Losses for Scene Geometry and Semantics", CVPR 2018.

```python
class MultiTaskLoss(nn.Module):
    def __init__(
        self,
        are_regression: List[bool] = [False, False],
        reduction: str = "none",
    )
```

### Parameters
- `are_regression` — Boolean list, one per task. `True` = regression task, `False` = classification task. Length determines number of tasks
- `reduction` — PyTorch reduction mode. Default: `"none"`

### How it works

Learns log-variance parameters (`log_vars`) per task. These are optimized jointly with the main model. The forward pass returns scaled losses:

```
coeff_i = 1 / ((is_regression_i + 1) * var_i)
scaled_loss_i = coeff_i * loss_i + log(std_i)
```

Classification tasks (regression=False) use coefficient `1/(2*var)`, regression uses `1/var`.

### forward()

```python
def forward(self, losses: List[Tensor]) -> List[Tensor]
```

- `losses` — List of per-task loss tensors, one per task

Returns list of scaled loss tensors (same length as input).

### Example

```python
import torch
import scitex as stx

are_regression = [False, False]  # Two classification tasks
mtl = stx.ai.MultiTaskLoss(are_regression)

# Include MTL parameters in optimizer
optimizer = torch.optim.Adam(
    list(model.parameters()) + list(mtl.parameters()),
    lr=1e-3,
)

# Training step
loss1 = cross_entropy(logits1, targets1)
loss2 = cross_entropy(logits2, targets2)

scaled = mtl([loss1, loss2])
total_loss = sum(scaled)
total_loss.backward()
optimizer.step()
```

### Important: mtl.parameters() must be optimized

The `log_vars` are `nn.Parameter` instances — include `mtl.parameters()` in your optimizer. If they are excluded, automatic weighting does not function.

---

## L1 / L2 / Elastic Regularization

Module-level regularization helpers in `scitex.ai.loss._L1L2Losses`.

```python
def l1(model, lambda_l1: float = 0.01) -> Tensor
def l2(model, lambda_l2: float = 0.01) -> Tensor
def elastic(model, alpha: float = 1.0, l1_ratio: float = 0.5) -> Tensor
```

### Parameters
- `model` — PyTorch `nn.Module`
- `lambda_l1` / `lambda_l2` — Regularization strength coefficient
- `alpha` — Total regularization strength for elastic net
- `l1_ratio` — Balance between L1 and L2 (0 = pure L2, 1 = pure L1)

### Note

These functions allocate on CUDA (`.cuda()` call inside). Intended for GPU training contexts. `elastic` combines L1 and L2:

```
elastic = alpha * (l1_ratio * L1 + (1 - l1_ratio) * L2)
```

### Example

```python
from scitex.ai.loss._L1L2Losses import l1, l2, elastic

# Add to loss during training
loss = criterion(outputs, targets)
loss = loss + l1(model, lambda_l1=0.001)
loss.backward()
```
