---
description: Classification metrics — balanced accuracy, MCC, confusion matrix, ROC-AUC, PR-AUC, silhouette scores, feature importance. All return dicts with metadata.
---

# Metrics

All functions in `stx.ai.metrics` return dictionaries containing `"metric"`, `"value"`, `"fold"`, and optionally `"labels"` or `"error"`.

## calc_bacc()

```python
def calc_bacc(
    y_true: np.ndarray,
    y_pred: np.ndarray,
    labels: Optional[List] = None,
    fold: Optional[int] = None,
) -> Dict[str, Any]
```

Balanced accuracy (average recall across classes).

### Return value
`{"metric": "balanced_accuracy", "value": float, "fold": int, "labels": list}`

### Example
```python
import scitex as stx

result = stx.ai.metrics.calc_bacc(y_true, y_pred)
print(f"Balanced accuracy: {result['value']:.3f}")
```

---

## calc_mcc()

```python
def calc_mcc(
    y_true: np.ndarray,
    y_pred: np.ndarray,
    labels: Optional[List] = None,
    fold: Optional[int] = None,
) -> Dict[str, Any]
```

Matthews Correlation Coefficient — ranges from -1 to +1.

---

## calc_conf_mat()

```python
def calc_conf_mat(
    y_true: np.ndarray,
    y_pred: np.ndarray,
    labels: Optional[List] = None,
    fold: Optional[int] = None,
    normalize: Optional[str] = None,
) -> Dict[str, Any]
```

### Parameters
- `normalize` — `"true"` (row-normalize), `"pred"` (column-normalize), `"all"` (total), or `None`

### Return value
`{"metric": "confusion_matrix", "value": pd.DataFrame, "fold": int, "labels": list, "normalize": ...}`

The `"value"` is a `pd.DataFrame` with class labels as both index and columns.

### Example
```python
result = stx.ai.metrics.calc_conf_mat(
    y_true, y_pred,
    labels=["Cat", "Dog", "Bird"],
    normalize="true",
)
print(result["value"])  # pd.DataFrame
```

---

## calc_roc_auc()

```python
def calc_roc_auc(
    y_true: np.ndarray,
    y_proba: np.ndarray,
    labels: Optional[List] = None,
    fold: Optional[int] = None,
    return_curve: bool = False,
) -> Dict[str, Any]
```

ROC AUC score. Handles binary and multiclass (OvR weighted average).

### Parameters
- `y_proba` — Probability array: shape `(n,)` for binary 1D, `(n, 2)` for binary 2-column, `(n, k)` for multiclass
- `return_curve` — Include FPR/TPR arrays in result (binary only)

### Return value
`{"metric": "roc_auc", "value": float, "fold": int}` and optionally `"curve": {"fpr": ..., "tpr": ..., "thresholds": ...}`

---

## calc_pre_rec_auc()

```python
def calc_pre_rec_auc(
    y_true: np.ndarray,
    y_proba: np.ndarray,
    labels: Optional[List] = None,
    fold: Optional[int] = None,
) -> Dict[str, Any]
```

Precision-Recall AUC score.

---

## calc_clf_report()

```python
def calc_clf_report(
    y_true: np.ndarray,
    y_pred: np.ndarray,
    labels: Optional[List] = None,
    fold: Optional[int] = None,
) -> Dict[str, Any]
```

Wraps `sklearn.metrics.classification_report`. The `"value"` is the formatted report string.

---

## calc_bacc_from_conf_mat()

```python
def calc_bacc_from_conf_mat(
    conf_mat: np.ndarray,
) -> float
```

Computes balanced accuracy directly from a confusion matrix array.

---

## Silhouette Scores

```python
# Block-based (efficient for large datasets)
calc_silhouette_score_block(X, labels, block_size=1000)
calc_silhouette_samples_block(X, labels, block_size=1000)

# Exact (slow for large datasets)
calc_silhouette_score_slow(X, labels)
calc_silhouette_samples_slow(X, labels)
```

All return float (score) or array (samples).

---

## Feature Importance

```python
# From model attributes (tree or linear)
calc_feature_importance(
    model,
    feature_names: List[str],
    method: str = "auto",  # "auto", "tree", "coef"
) -> Optional[Dict[str, float]]

# Permutation-based
calc_permutation_importance(
    model,
    X_val: np.ndarray,
    y_val: np.ndarray,
    feature_names: List[str],
    n_repeats: int = 10,
) -> Dict[str, float]
```

---

## Seizure Prediction Metrics (Domain-specific)

```python
calc_seizure_window_prediction_metrics(y_true, y_pred, ...)
calc_seizure_event_prediction_metrics(y_true, y_pred, ...)
calc_seizure_prediction_metrics(...)  # Backward compat alias
```

Specialized metrics for event-based seizure prediction evaluation.

---

## Full import reference

```python
from scitex.ai.metrics import (
    calc_bacc,
    calc_mcc,
    calc_conf_mat,
    calc_clf_report,
    calc_roc_auc,
    calc_pre_rec_auc,
    calc_bacc_from_conf_mat,
    calc_silhouette_score_block,
    calc_silhouette_score_slow,
    calc_silhouette_samples_block,
    calc_silhouette_samples_slow,
    calc_feature_importance,
    calc_permutation_importance,
    calc_seizure_window_prediction_metrics,
    calc_seizure_event_prediction_metrics,
)
```
