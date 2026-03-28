# SQLite3 Database with stx.db

`stx.db.SQLite3` is a high-level SQLite3 wrapper with automatic compression, numpy array storage, thread-safe operations, and context manager support.

## Basic Usage

```python
from scitex.db import SQLite3

# Recommended: use as context manager
with SQLite3("experiments.db", compress_by_default=True) as db:
    # Create table
    db.create_table(
        "experiments",
        {"id": "INTEGER PRIMARY KEY", "name": "TEXT", "value": "REAL"}
    )

    # Insert rows
    db.insert("experiments", {"name": "run_1", "value": 3.14})

    # Query
    rows = db.select("experiments", where="value > 3.0")
    for row in rows:
        print(row)

    # Execute raw SQL
    db.execute("UPDATE experiments SET value = 0 WHERE name = 'run_1'")
```

## Numpy Array Storage (ArrayMixin)

The `_ArrayMixin` provides BLOB storage with automatic compression (70-90% size reduction):

```python
import numpy as np

with SQLite3("arrays.db") as db:
    db.create_table(
        "measurements",
        {
            "id": "INTEGER PRIMARY KEY",
            "name": "TEXT",
            "timestamp": "INTEGER",
            "data": "BLOB"
        }
    )

    # Save numpy array as compressed BLOB
    data = np.random.random((1000, 100))
    db.save_array(
        table_name="measurements",
        data=data,
        column="data",
        additional_columns={"name": "experiment_1", "timestamp": 1234567890}
    )

    # Load array back
    loaded = db.load_array(
        "measurements",
        column="data",
        where="name = 'experiment_1'"
    )
    # loaded.shape == (1000, 100)
```

## Mixin Capabilities

`SQLite3` inherits from these mixins:

| Mixin | Key methods |
|-------|-------------|
| `_ArrayMixin` | `save_array`, `load_array` |
| `_ConnectionMixin` | `connect`, `close`, `execute` |
| `_QueryMixin` | `select`, `count`, `exists` |
| `_TransactionMixin` | `begin`, `commit`, `rollback` |
| `_ColumnMixin` | `add_column`, `list_columns` |
| `_TableMixin` | `create_table`, `drop_table`, `list_tables` |
| `_IndexMixin` | `create_index`, `drop_index` |
| `_RowMixin` | `insert`, `update`, `delete`, `upsert` |
| `_BatchMixin` | `batch_insert`, `batch_update` |
| `_BlobMixin` | `save_blob`, `load_blob` |
| `_ImportExportMixin` | `import_csv`, `export_csv` |
| `_MaintenanceMixin` | `vacuum`, `analyze`, `integrity_check` |
| `_GitMixin` | git-based database versioning |

## Health Checks and Maintenance

```python
from scitex.db import check_health, batch_health_check

# Single database
health = check_health("experiments.db")

# Multiple databases
all_health = batch_health_check(["db1.db", "db2.db", "db3.db"])
```

## Removing Duplicates

```python
from scitex.db import delete_sqlite3_duplicates, delete_duplicates

# SQLite3-specific helper
delete_sqlite3_duplicates("experiments.db", table="results", key_cols=["session_id"])

# Generic version (works with any db instance)
delete_duplicates(db_instance, table="results", key_cols=["session_id"])
```

## Schema Inspection

```python
from scitex.db import inspect

schema = inspect("experiments.db")
print(schema)  # Shows tables, columns, types, indexes
```
