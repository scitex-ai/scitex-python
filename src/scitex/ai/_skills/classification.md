---
description: Classification utilities — Classifier factory, ClassificationReporter for metric tracking and visualization, CrossValidationExperiment for full CV pipelines.
---

# Classification

## Classifier

Factory class that initializes scikit-learn classifiers with a consistent interface.

```python
class Classifier:
    def __init__(
        self,
        class_weight: Optional[Dict[int, float]] = None,
        random_state: int = 42,
    )

    def __call__(
        self,
        clf_str: str,
        scaler: Optional[BaseEstimator] = None,
    ) -> Union[BaseEstimator, Pipeline]
```

### Parameters
- `class_weight` — Class weight dict (e.g. `{0: 1.0, 1: 2.0}`) for imbalanced data. Default: `None`
- `random_state` — Reproducibility seed. Default: `42`

### Calling `__call__`
- `clf_str` — Name of classifier to instantiate (see list below)
- `scaler` — Optional sklearn scaler; if provided, wraps classifier in `Pipeline`

### Available classifiers
`"Perceptron"`, `"PassiveAggressiveClassifier"`, `"LogisticRegression"`, `"SGDClassifier"`, `"RidgeClassifier"`, `"QuadraticDiscriminantAnalysis"`, `"GaussianProcessClassifier"`, `"KNeighborsClassifier"`, `"AdaBoostClassifier"`, `"LinearSVC"`, `"SVC"`

### Classifier.list property
```python
clf_server.list  # -> List[str] of available classifier names
```

### Example
```python
import scitex as stx
from sklearn.preprocessing import StandardScaler

clf_server = stx.ai.Classifier(class_weight={0: 1.0, 1: 2.0})
clf = clf_server("SVC", scaler=StandardScaler())
clf.fit(X_train, y_train)
```

---

## ClassificationReporter

Tracks metrics for single-task and multi-task classification, generates visualizations and reports.

```python
class ClassificationReporter:
    def __init__(
        self,
        output_dir: Union[str, Path],
        tasks: Optional[List[str]] = None,
        precision: int = 3,
        required_metrics: Optional[List[str]] = [...],
        verbose: bool = True,
        **kwargs,
    )
```

### Parameters
- `output_dir` — Base directory for all outputs (created automatically)
- `tasks` — List of task names for multi-task mode; `None` for single-task mode
- `precision` — Decimal places for numerical outputs. Default: `3`
- `required_metrics` — Metrics to calculate. Default includes: `"balanced_accuracy"`, `"mcc"`, `"confusion_matrix"`, `"classification_report"`, `"roc_auc"`, `"roc_curve"`, `"pre_rec_auc"`, `"pre_rec_curve"`
- `verbose` — Print initialization messages. Default: `True`

### calculate_metrics()

```python
def calculate_metrics(
    self,
    y_true: np.ndarray,
    y_pred: np.ndarray,
    y_proba: Optional[np.ndarray] = None,
    labels: Optional[List[str]] = None,
    fold: Optional[int] = None,
    task: Optional[str] = None,
    verbose: bool = True,
    model=None,
    feature_names: Optional[List[str]] = None,
) -> Dict[str, Any]
```

- `y_true` — True class labels
- `y_pred` — Predicted class labels
- `y_proba` — Prediction probabilities (required for AUC metrics)
- `labels` — Class label names for display
- `fold` — Fold index for cross-validation
- `task` — Task identifier for multi-task mode (created dynamically if new)
- `model` — Fitted model for automatic feature importance extraction
- `feature_names` — Feature names (required when `model` is passed)

### save_summary()

```python
def save_summary(
    self,
    filename: str = "summary.json",
    verbose: bool = True,
) -> Path
```

Saves metrics summary and triggers CV aggregation plots (with faded fold lines) if folds were tracked.

### save_feature_importance()

```python
def save_feature_importance(
    self,
    model,
    feature_names: List[str],
    fold: Optional[int] = None,
    task: Optional[str] = None,
) -> Dict[str, float]
```

### Example — Single task with cross-validation

```python
import scitex as stx
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import StratifiedKFold

reporter = stx.ai.ClassificationReporter("./results/binary")

cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
model = LogisticRegression()

for fold, (train_idx, test_idx) in enumerate(cv.split(X, y)):
    model.fit(X[train_idx], y[train_idx])
    y_pred = model.predict(X[test_idx])
    y_proba = model.predict_proba(X[test_idx])
    reporter.calculate_metrics(
        y_true=y[test_idx],
        y_pred=y_pred,
        y_proba=y_proba,
        labels=["Negative", "Positive"],
        fold=fold,
    )

reporter.save_summary()
```

### Example — Multi-task

```python
reporter = stx.ai.ClassificationReporter(
    "./results/multitask",
    tasks=["task_a", "task_b"],
)
reporter.calculate_metrics(y_true_a, y_pred_a, task="task_a", fold=0)
reporter.calculate_metrics(y_true_b, y_pred_b, task="task_b", fold=0)
reporter.save_summary()
```

---

## CrossValidationExperiment

High-level helper that runs a full CV experiment from a model factory function.

```python
class CrossValidationExperiment:
    def __init__(
        self,
        name: str,
        model_fn: Callable,
        cv: Optional[BaseCrossValidator] = None,
        output_dir: Optional[Union[str, Path]] = None,
        metrics: Optional[List[str]] = None,
        save_models: bool = True,
        verbose: bool = True,
    )
```

### Parameters
- `name` — Experiment name (used in output paths)
- `model_fn` — Callable that returns a fresh model instance per fold
- `cv` — Splitter instance. Default: `StratifiedKFold(n_splits=5, shuffle=True, random_state=42)`
- `save_models` — Whether to pickle models per fold. Default: `True`

### run()

```python
def run(
    self,
    X: np.ndarray,
    y: np.ndarray,
    feature_names: Optional[List[str]] = None,
    class_names: Optional[List[str]] = None,
    calculate_curves: bool = True,
) -> Dict[str, Any]
```

Returns dict with `"paths"`, `"metadata"`, `"timing"`, `"models"`.

### Example

```python
import scitex as stx
from sklearn.svm import SVC

experiment = stx.ai.CrossValidationExperiment(
    name="svm_binary",
    model_fn=lambda: SVC(probability=True),
    output_dir="./cv_results",
)
results = experiment.run(X, y, class_names=["Neg", "Pos"])
```

### quick_experiment()

Convenience function for rapid experimentation:

```python
from scitex.ai.classification import quick_experiment

results = quick_experiment(
    X, y, model=SVC(), name="quick_svm", n_folds=5
)
```

---

## Time Series CV Splitters

Available in `stx.ai.classification.timeseries`:

| Class | Description |
|---|---|
| `TimeSeriesStratifiedSplit` | Stratified split preserving class balance in time series |
| `TimeSeriesBlockingSplit` | Non-overlapping block CV for time series |
| `TimeSeriesSlidingWindowSplit` | Rolling/expanding window CV |
| `TimeSeriesCalendarSplit` | Split by calendar period (day/week/month) |
| `TimeSeriesStrategy` | Strategy pattern for flexible splitter selection |
| `TimeSeriesMetadata` | Metadata container for time series datasets |

```python
from scitex.ai.classification.timeseries import TimeSeriesSlidingWindowSplit

splitter = TimeSeriesSlidingWindowSplit(n_splits=5)
for train_idx, test_idx in splitter.split(X, y):
    ...
```
