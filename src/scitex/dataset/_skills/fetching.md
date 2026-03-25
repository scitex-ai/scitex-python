---
name: dataset-fetching
description: Retrieve dataset listings from OpenNeuro and other sources using fetch_datasets(), fetch_all_datasets(), and format individual dataset entries with format_dataset().
---

# Dataset Fetching

## fetch_datasets

Fetch a page of datasets from a source repository.

```python
fetch_datasets(source: str = "openneuro", page: int = 1, per_page: int = 25) -> list[dict]
```

```python
import scitex as stx

datasets = stx.dataset.fetch_datasets(source="openneuro", per_page=10)
for ds in datasets:
    print(ds["id"], ds["name"])
```

---

## fetch_all_datasets

Fetch all available datasets up to a limit.

```python
fetch_all_datasets(source: str = "openneuro", max_datasets: int = 100) -> list[dict]
```

```python
import scitex as stx

all_datasets = stx.dataset.fetch_all_datasets(max_datasets=50)
print(f"Fetched {len(all_datasets)} datasets")
```

---

## format_dataset

Normalize a raw dataset dict into a consistent schema.

```python
format_dataset(raw: dict) -> dict
```

```python
import scitex as stx

datasets = stx.dataset.fetch_datasets()
formatted = [stx.dataset.format_dataset(d) for d in datasets]
# Each formatted entry has: id, name, description, modality, subjects, url
```

---

## OPENNEURO_API

Base URL constant for the OpenNeuro GraphQL API.

```python
import scitex as stx

print(stx.dataset.OPENNEURO_API)
# 'https://openneuro.org/crn/graphql'
```
