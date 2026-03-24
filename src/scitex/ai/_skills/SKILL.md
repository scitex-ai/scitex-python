---
name: stx.ai
description: Machine learning and artificial intelligence utilities for classification, clustering, training, and GenAI integration.
---

# stx.ai

The `stx.ai` module provides machine learning utilities for scientific research, including classification pipelines, clustering, feature extraction, and training helpers. It also provides a lazy-loaded `GenAI` class for integrating with large language models.

## Python API

```python
import scitex as stx

# Classification
classifier = stx.ai.Classifier(model, num_classes=3)
reporter = stx.ai.ClassificationReporter()

# Training helpers
early_stopping = stx.ai.EarlyStopping(patience=10)
logger = stx.ai.LearningCurveLogger()

# Optimizer
optimizer = stx.ai.get_optimizer(model, "adam", lr=1e-3)

# Multi-task loss
loss_fn = stx.ai.MultiTaskLoss(task_weights=[1.0, 0.5])

# GenAI (lazy-loaded)
gen = stx.ai.GenAI(model="claude-3-5-sonnet")
response = gen.chat("Summarize this paper...")

# Submodules
stx.ai.activation    # Activation functions
stx.ai.clustering    # Clustering algorithms
stx.ai.metrics       # Classification metrics (calc_bacc, etc.)
stx.ai.sampling      # Data sampling utilities
stx.ai.sklearn       # Scikit-learn integrations
```

## Key Features

- `Classifier` and `ClassificationReporter` for end-to-end classification workflows
- `EarlyStopping` with configurable patience for training loops
- `LearningCurveLogger` for tracking training/validation metrics
- `MultiTaskLoss` for multi-objective optimization
- `GenAI` for LLM integration (lazy-loaded to avoid heavy imports)
- Submodules: `activation`, `clustering`, `feature_extraction`, `loss`, `metrics`, `optim`, `sampling`, `sklearn`, `training`
