---
name: dataset-database
description: Build a local SQLite dataset cache with db.build(), run fast offline keyword search with db.search(), and inspect the cache with db.stats().
---

# Local Dataset Database

`stx.dataset.db` (alias for `stx.dataset.database`) wraps a local SQLite cache for fast offline dataset search.

## db.build

Fetch all datasets from all configured sources and store them in the local cache.

```python
stx.dataset.db.build()
```

This is a one-time setup step. The database is stored at `~/.scitex/datasets/cache.db`.

```python
import scitex as stx

# Build the local cache (takes a few minutes on first run)
stx.dataset.db.build()
```

---

## db.search

Run a keyword search against the local cache.

```python
stx.dataset.db.search(query: str, limit: int = 20) -> list[dict]
```

```python
import scitex as stx

results = stx.dataset.db.search("EEG epilepsy")
for r in results:
    print(r["id"], r["name"])
```

---

## db.stats

Return statistics about the local cache (record count, sources, last update time).

```python
stx.dataset.db.stats() -> dict
```

```python
import scitex as stx

info = stx.dataset.db.stats()
print(info)
# {'total': 4523, 'sources': ['openneuro', 'physionet', 'dandi'], 'last_updated': '...'}
```
