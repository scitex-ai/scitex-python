---
description: stx.ml is a backward-compatibility alias for stx.ai. Submodule mapping and migration guidance.
---

# stx.ml Alias

`stx.ml` re-exports everything from `stx.ai`. Use `stx.ai` for new code; `stx.ml` is kept for backward compatibility.

## Submodule mapping

| `stx.ml.*` | `stx.ai.*` | Description |
|-----------|-----------|-------------|
| `classification` | `classification` | Classification utilities |
| `metrics` | `metrics` | ML metrics (bacc, auc, etc.) |
| `training` | `training` | Training loop helpers |
| `clustering` | `clustering` | Clustering algorithms |
| `feature_selection` | `feature_selection` | Feature selection |
| `feature_extraction` | `feature_extraction` | Feature extraction |
| `loss` | `loss` | Custom loss functions |
| `optim` | `optim` | Optimizer wrappers |
| `activation` | `activation` | Activation functions |
| `sklearn` / `sk` | `sklearn` / `sk` | scikit-learn wrappers |
| `utils` | `utils` | Shared utilities |
| `plt` | `plt` | ML-specific plots |

```python
import scitex as stx

# These are equivalent:
stx.ml.metrics.calc_bacc(y_true, y_pred)
stx.ai.metrics.calc_bacc(y_true, y_pred)
```
