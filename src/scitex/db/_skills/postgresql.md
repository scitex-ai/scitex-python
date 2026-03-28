---
description: PostgreSQL database wrapper with schema management, batch operations, blob storage, connection pooling, backup, and maintenance.
---

# PostgreSQL

`stx.db.PostgreSQL` — full PostgreSQL client.

```python
import scitex as stx

db = stx.db.PostgreSQL(
    host="localhost",
    port=5432,
    database="mydb",
    user="researcher",
    password="secret",
)
```

## Connection

```python
db.connect()
db.disconnect()

# Or use as context manager
with stx.db.PostgreSQL(...) as db:
    rows = db.fetch_all("results")
```

## Table and Schema operations

```python
db.create_table("results", {"id": "SERIAL PRIMARY KEY", "score": "FLOAT"})
db.create_schema("analysis")
db.list_schemas()
db.list_tables(schema="analysis")
```

## Row operations

```python
db.insert("results", {"score": 0.92})
db.insert_many("results", [{"score": s} for s in scores])
rows = db.fetch_all("results")
db.update("results", {"score": 0.95}, where={"id": 1})
db.delete("results", where={"id": 1})
```

## Batch operations

```python
# Bulk insert with conflict handling
db.upsert("results", rows, conflict_columns=["id"])
```

## Blob storage

```python
import numpy as np

arr = np.random.rand(100)
db.store_blob("blobs", "my_array", arr)
loaded = db.load_blob("blobs", "my_array")
```

## Backup

```python
db.backup("backup_20260325.sql")
db.restore("backup_20260325.sql")
```

## Index management

```python
db.create_index("results", columns=["score"], unique=False)
db.list_indexes("results")
```
