---
description: SQLite3 database wrapper with table management, row CRUD, query, transaction, array storage, git integration, and import/export capabilities.
---

# SQLite3

`stx.db.SQLite3` — file-based relational database.

```python
import scitex as stx

db = stx.db.SQLite3("experiment.db")
```

## Table operations

```python
# Create table
db.create_table("results", {"id": "INTEGER PRIMARY KEY", "score": "REAL", "label": "TEXT"})

# Check existence
db.table_exists("results")  # True/False

# List tables
db.list_tables()  # ['results', ...]

# Drop table
db.drop_table("results")
```

## Row operations

```python
# Insert
db.insert("results", {"score": 0.92, "label": "cat"})

# Insert many (batch)
rows = [{"score": s, "label": l} for s, l in zip(scores, labels)]
db.insert_many("results", rows)

# Fetch all rows
rows = db.fetch_all("results")  # list of dicts

# Fetch by condition
hits = db.fetch_where("results", {"label": "cat"})
```

## Query

```python
# Raw SQL
results = db.execute("SELECT * FROM results WHERE score > 0.8")
```

## Transaction

```python
with db.transaction():
    db.insert("results", {"score": 0.91, "label": "dog"})
    db.insert("results", {"score": 0.88, "label": "cat"})
```

## Array storage (SQLite3-specific)

Stores NumPy arrays as BLOBs with automatic serialization.

```python
import numpy as np

arr = np.random.rand(100, 64)
db.store_array("arrays", "my_feature", arr)
loaded = db.load_array("arrays", "my_feature")
```

## Git integration (SQLite3-specific)

Auto-commit the `.db` file to git after modifications.

```python
db_git = stx.db.SQLite3("experiment.db", auto_git_commit=True)
db_git.insert("results", {"score": 0.95})  # triggers git commit
```

## Import/Export

```python
db.export_to_csv("results", "results_backup.csv")
db.import_from_csv("results", "results_backup.csv")
```
