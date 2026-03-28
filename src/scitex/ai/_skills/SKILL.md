---
name: stx.ai
description: Machine learning and AI utilities — classification, clustering, GenAI, training helpers, metrics, and optimizer management.
---

# stx.ai

Machine learning and AI utilities for scientific research.

## Sub-skills

* [genai.md](genai.md) — GenAI unified LLM interface, providers, cost tracking
* [classification.md](classification.md) — Classifier, ClassificationReporter, CrossValidationExperiment
* [training.md](training.md) — EarlyStopping, LearningCurveLogger
* [loss.md](loss.md) — MultiTaskLoss, L1/L2/Elastic regularization
* [optim.md](optim.md) — get_optimizer, set_optimizer, Ranger support
* [clustering.md](clustering.md) — pca(), umap() dimensionality reduction
* [metrics.md](metrics.md) — calc_bacc, calc_conf_mat, calc_roc_auc, silhouette scores
* [sampling.md](sampling.md) — undersample() for imbalanced data
* [feature-selection.md](feature-selection.md) — extract_feature_importance, select_features_univariate

## Quick Reference

```python
import scitex as stx

# GenAI (lazy-loaded)
gen = stx.ai.GenAI(model="gpt-4o")
response = gen("Summarize this experiment...")

# Classification
clf_server = stx.ai.Classifier(class_weight={0: 1.0, 1: 2.0})
clf = clf_server("SVC")
reporter = stx.ai.ClassificationReporter("./results")
reporter.calculate_metrics(y_true, y_pred, y_proba)

# Training
early_stopping = stx.ai.EarlyStopping(patience=10, direction="minimize")
logger = stx.ai.LearningCurveLogger()

# Loss
mtl = stx.ai.MultiTaskLoss(are_regression=[False, False])

# Optimizer
optimizer = stx.ai.set_optimizer(model, "adam", lr=1e-3)

# Metrics
result = stx.ai.metrics.calc_bacc(y_true, y_pred)
cm = stx.ai.metrics.calc_conf_mat(y_true, y_pred)
```
