---
description: Dimensionality reduction and visualization — pca() and umap() with multi-dataset subplot support, optional supervised mode, and independent legend export.
---

# Clustering / Dimensionality Reduction

## pca()

```python
def pca(
    data_all: list,
    labels_all: list,
    axes_titles: Optional[list] = None,
    title: str = "PCA Clustering",
    alpha: float = 0.1,
    s: int = 3,
    use_independent_legend: bool = False,
    add_super_imposed: bool = False,
    palette: str = "viridis",
) -> Tuple[Figure, Optional[List[Figure]], PCA]
```

### Parameters
- `data_all` — List of data arrays; first is used to fit PCA, rest are transformed
- `labels_all` — List of label arrays corresponding to `data_all`
- `axes_titles` — Titles for each subplot
- `title` — Super-title for the figure
- `alpha` — Point transparency
- `s` — Scatter point size
- `use_independent_legend` — Export legends as separate figures
- `add_super_imposed` — Add a first subplot showing all datasets superimposed
- `palette` — Seaborn color palette name

### Return value
`(fig, legend_figs_or_None, pca_model)`

- `fig` — Matplotlib figure
- `legend_figs_or_None` — List of legend figures when `use_independent_legend=True`, else `None`
- `pca_model` — Fitted `sklearn.decomposition.PCA` object (2 components)

### Example

```python
import scitex as stx
from sklearn.datasets import load_iris

dataset = load_iris()
X, y = dataset.data, dataset.target

fig, _, pca_model = stx.ai.clustering.pca(
    data_all=[X],
    labels_all=[y],
    title="Iris PCA",
    s=10,
    alpha=0.5,
)
stx.io.save(fig, "./iris_pca.png")
```

### Multi-dataset example

```python
from sklearn.model_selection import train_test_split

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3)

fig, legends, pca_model = stx.ai.clustering.pca(
    data_all=[X_train, X_test],
    labels_all=[y_train, y_test],
    axes_titles=["Train", "Test"],
    title="Train vs Test PCA",
    use_independent_legend=True,
    add_super_imposed=True,
)
```

---

## umap()

```python
def umap(
    data: list,
    labels: list,
    hues: Optional[list] = None,
    hues_colors: Optional[list] = None,
    axes=None,
    axes_titles: Optional[list] = None,
    supervised: bool = False,
    title: str = "UMAP Clustering",
    alpha: float = 1.0,
    s: int = 3,
    use_independent_legend: bool = False,
    add_super_imposed: bool = False,
    umap_model=None,
) -> Tuple[Figure, Optional[List[Figure]], UMAP]
```

### Parameters
- `data` — List of data arrays; first is used to fit UMAP
- `labels` — List of label arrays
- `hues` — Optional list of custom hue arrays (overrides labels for coloring)
- `hues_colors` — Optional list of color arrays matching `hues`
- `axes` — Existing matplotlib axes to plot into
- `supervised` — Use supervised UMAP (labels used in fitting). Default: `False`
- `umap_model` — Pre-fitted UMAP model; if provided, skips fitting

### Return value
`(fig, legend_figs_or_None, umap_model)`

### Requires
```bash
pip install umap-learn
```

### Example

```python
import scitex as stx
from sklearn.datasets import load_digits

dataset = load_digits()
X, y = dataset.data, dataset.target

fig, _, umap_model = stx.ai.clustering.umap(
    data=[X],
    labels=[y],
    supervised=False,
    title="Digits UMAP",
    s=5,
    alpha=0.8,
)
stx.io.save(fig, "./digits_umap.png")
```

### Supervised UMAP

```python
fig, _, umap_model = stx.ai.clustering.umap(
    data=[X_train, X_test],
    labels=[y_train, y_test],
    supervised=True,
    axes_titles=["Train", "Test"],
    title="Supervised UMAP",
)
# umap_model.transform(new_data) works after fitting
```
