---
description: Feature selection utilities — extract importance from models, univariate selection, cross-fold consistency analysis, and importance aggregation.
---

# Feature Selection

Available in `scitex.ai.feature_selection`.

## extract_feature_importance()

```python
def extract_feature_importance(
    model,
    feature_names: List[str],
    method: str = "auto",
) -> Optional[Dict[str, float]]
```

Extracts and normalizes feature importance from a trained model.

### Parameters
- `model` — Trained scikit-learn estimator
- `feature_names` — List of feature name strings
- `method` — Extraction method:
  - `"auto"` — Use `feature_importances_` if available, else `coef_`, else warn and return `None`
  - `"tree"` — Use `model.feature_importances_` (RandomForest, GradientBoosting, etc.)
  - `"coef"` — Use `model.coef_` absolute values (LogisticRegression, SVM, etc.); averages across classes for multiclass

### Return value
`Dict[str, float]` sorted by importance descending (normalized to sum 1.0), or `None` if extraction fails.

### Example

```python
from sklearn.ensemble import RandomForestClassifier
from scitex.ai.feature_selection import extract_feature_importance

model = RandomForestClassifier().fit(X_train, y_train)
importances = extract_feature_importance(model, feature_names)
# {"feature_3": 0.25, "feature_1": 0.18, ...}
```

---

## select_features_univariate()

```python
def select_features_univariate(
    X_train: np.ndarray,
    y_train: np.ndarray,
    X_val: np.ndarray,
    feature_names: List[str],
    k: int = 10,
    score_func: str = "f_classif",
    impute_strategy: str = "median",
) -> Tuple[np.ndarray, np.ndarray, List[int], List[str], object]
```

Selects top-k features using univariate statistical tests. Fits selector **only on training data** to prevent data leakage.

### Parameters
- `k` — Number of features to select (capped at `X_train.shape[1]`)
- `score_func` — Statistical test:
  - `"f_classif"` — ANOVA F-test (default, works with any continuous features)
  - `"chi2"` — Chi-squared (requires non-negative features)
  - `"mutual_info"` — Mutual information
- `impute_strategy` — Missing value imputation: `"median"` (default), `"mean"`, `"most_frequent"`, `"constant"`

### Return value
`(X_train_selected, X_val_selected, feature_indices, selected_names, imputer)`

Apply imputer to test data: `imputer.transform(X_test)`.

### Example

```python
from scitex.ai.feature_selection import select_features_univariate

X_tr_sel, X_val_sel, indices, names, imputer = select_features_univariate(
    X_train, y_train, X_val, feature_names, k=20
)
X_test_imputed = imputer.transform(X_test)
```

---

## analyze_feature_consistency()

```python
def analyze_feature_consistency(
    selected_features_per_fold: List[List[str]],
) -> Dict[str, Union[int, float, Dict[str, int]]]
```

Analyzes which features are consistently selected across CV folds.

### Return value
```python
{
    "feature_frequency": {"feature_name": count, ...},
    "n_folds": int,
    "n_unique_features": int,
    "consistency_score": float,   # 0-1; 1.0 = same features every fold
    "stable_features": [...],     # Selected in ALL folds
    "unstable_features": [...],   # Selected in only ONE fold
}
```

---

## aggregate_feature_importances()

```python
def aggregate_feature_importances(
    importances_per_fold: List[Dict[str, float]],
    method: str = "mean",
) -> Dict[str, Dict[str, float]]
```

Aggregates feature importance dicts across CV folds.

### Return value
```python
{
    "mean": {"feature": value, ...},
    "std": {"feature": value, ...},
    "min": {"feature": value, ...},
    "max": {"feature": value, ...},
    "cv":  {"feature": value, ...},  # Coefficient of variation
}
```

---

## create_feature_importance_dataframe()

```python
def create_feature_importance_dataframe(
    aggregated_importances: Dict[str, Dict[str, float]],
) -> pd.DataFrame
```

Converts aggregated importance dict (from `aggregate_feature_importances`) to a sorted DataFrame with columns: `feature`, `mean`, `std`, `min`, `max`, `cv`.

### Example — Full CV workflow

```python
from scitex.ai.feature_selection import (
    extract_feature_importance,
    aggregate_feature_importances,
    create_feature_importance_dataframe,
    analyze_feature_consistency,
)

importances_per_fold = []
selected_per_fold = []

for fold, (train_idx, test_idx) in enumerate(cv.split(X, y)):
    model.fit(X[train_idx], y[train_idx])
    imp = extract_feature_importance(model, feature_names)
    importances_per_fold.append(imp)
    selected_per_fold.append(list(imp.keys())[:10])

# Aggregate
aggregated = aggregate_feature_importances(importances_per_fold)
df = create_feature_importance_dataframe(aggregated)
print(df.head(10))

# Consistency
consistency = analyze_feature_consistency(selected_per_fold)
print(f"Stable features: {consistency['stable_features']}")
```
