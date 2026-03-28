---
description: Filter datasets by modality, keyword, or metadata with search_datasets() and rank results with sort_datasets().
---

# Dataset Search

## search_datasets

Filter a list of dataset dicts by search criteria.

```python
search_datasets(
    datasets: list[dict],
    query: str | None = None,
    modality: str | None = None,
    min_subjects: int | None = None,
) -> list[dict]
```

```python
import scitex as stx

all_ds = stx.dataset.fetch_all_datasets(max_datasets=200)

# Search by modality
eeg_datasets = stx.dataset.search_datasets(all_ds, modality="eeg")

# Search by keyword
alzheimer_ds = stx.dataset.search_datasets(all_ds, query="alzheimer")

# Combine filters
large_eeg = stx.dataset.search_datasets(
    all_ds, modality="eeg", min_subjects=50
)
```

---

## sort_datasets

Sort datasets by a field (e.g., number of subjects or name).

```python
sort_datasets(
    datasets: list[dict],
    by: str = "subjects",
    ascending: bool = False,
) -> list[dict]
```

```python
import scitex as stx

all_ds = stx.dataset.fetch_all_datasets()
sorted_ds = stx.dataset.sort_datasets(all_ds, by="subjects", ascending=False)

# Top 5 largest datasets
for ds in sorted_ds[:5]:
    print(ds["name"], ds.get("subjects"))
```
