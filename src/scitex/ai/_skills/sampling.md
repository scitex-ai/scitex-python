---
description: Data sampling utilities — undersample() for class-balanced random undersampling of imbalanced datasets.
---

# Sampling

## undersample()

```python
def undersample(
    X: ArrayLike,
    y: ArrayLike,
    random_state: int = 42,
) -> Tuple[ArrayLike, ArrayLike]
```

Randomly undersamples the majority class(es) to balance class distribution. Preserves the input data type.

### Parameters
- `X` — Features, shape `(n_samples, n_features)`
- `y` — Labels, shape `(n_samples,)`
- `random_state` — Seed for reproducibility. Default: `42`

### Return value
`(X_resampled, y_resampled)` — same type as inputs, with balanced classes.

### Requires
```bash
pip install imbalanced-learn
```

Raises `ImportError` if `imbalanced-learn` is not installed.

### Example

```python
import scitex as stx
import numpy as np

# Imbalanced dataset: 900 class 0, 100 class 1
X = np.random.randn(1000, 10)
y = np.array([0] * 900 + [1] * 100)

X_balanced, y_balanced = stx.ai.sampling.undersample(X, y)
# X_balanced.shape[0] == 200 (100 from each class)
```

### Note on alternative approaches

For oversampling (SMOTE etc.) or more advanced strategies, use `imbalanced-learn` directly. `undersample()` is a thin wrapper around `imblearn.under_sampling.RandomUnderSampler`.
