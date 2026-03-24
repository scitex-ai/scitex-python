---
name: stx.dataset
description: Scientific dataset discovery and access for neuroscience (OpenNeuro, PhysioNet, DANDI) and general domains.
---

# stx.dataset

The `stx.dataset` module provides access to scientific dataset discovery and download across multiple public repositories. It supports local database indexing for fast search and integrates with OpenNeuro, PhysioNet, DANDI, and other neuroscience archives.

## Python API

```python
import scitex as stx

# Discover datasets across all sources
datasets = stx.dataset.fetch_all_datasets(max_datasets=100)

# Search by modality or keyword
results = stx.dataset.search_datasets(datasets, modality="eeg")

# Build a local searchable database
stx.dataset.db.build()
results = stx.dataset.db.search("alzheimer EEG")
stats = stx.dataset.db.stats()

# Domain-specific fetching
neuro_datasets = stx.dataset.fetch_datasets(source="openneuro", max_datasets=50)

# Format a single dataset for display
formatted = stx.dataset.format_dataset(dataset)

# Sort datasets by relevance
sorted_ds = stx.dataset.sort_datasets(datasets, key="n_subjects")
```

## Key Features

- `fetch_all_datasets` / `fetch_datasets` — discover datasets from multiple public archives
- `search_datasets` — filter by modality, keyword, or metadata
- `database` / `db` — local SQLite index for fast offline search
- Domain submodules: `neuroscience`, `general`
- Supported sources: OpenNeuro, PhysioNet, DANDI
- Delegates to `scitex-dataset` package
