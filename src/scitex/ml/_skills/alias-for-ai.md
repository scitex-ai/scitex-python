---
description: stx.ml is a backward-compatibility re-export of scitex.ai. New code should use stx.ai.
---

# stx.ml — Alias for stx.ai

`scitex.ml` is a thin shim that does `from scitex.ai import *`. All functionality lives in `scitex.ai`. The `ml` name exists for code written before the module was renamed.

## Migration

```python
# Old (still works)
from scitex.ml import classification, metrics, training

# New (preferred)
from scitex.ai import classification, metrics, training
```

## Available submodules (from scitex.ai)

```python
import scitex as stx

stx.ml.classification        # Classifiers, cross-validation
stx.ml.clustering            # K-means, DBSCAN, etc.
stx.ml.feature_extraction    # PCA, feature engineering
stx.ml.feature_selection     # Selector utilities
stx.ml.metrics               # calc_bacc, confusion matrix, etc.
stx.ml.training              # Early stopping, train loops
stx.ml.optim                 # Optimizer wrappers
stx.ml.activation            # Activation functions
stx.ml.loss                  # Loss functions
stx.ml.sklearn / stx.ml.sk   # scikit-learn helpers
stx.ml.utils                 # Shared utilities
stx.ml.plt                   # ML-specific plotting
```

For full documentation on each submodule, see the `stx.ai` skills.
