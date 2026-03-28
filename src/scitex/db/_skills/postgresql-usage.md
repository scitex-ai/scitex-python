# PostgreSQL Database with stx.db

`stx.db.PostgreSQL` is a high-level PostgreSQL wrapper with the same mixin architecture as `SQLite3`.

## Connection

```python
from scitex.db import PostgreSQL

db = PostgreSQL(
    host="localhost",
    port=5432,
    dbname="mydb",
    user="user",
    password="secret",
)
db.connect()

# Or as context manager
with PostgreSQL(host="localhost", dbname="mydb", user="user") as db:
    rows = db.select("experiments", where="status = 'pending'")
    for row in rows:
        print(row)

db.close()
```

## Core Operations

```python
with PostgreSQL(host="localhost", dbname="mydb", user="user") as db:
    # Raw SQL execution
    result = db.execute("SELECT COUNT(*) FROM experiments")

    # High-level row operations
    db.insert("experiments", {"name": "run_42", "status": "running"})
    db.update("experiments", {"status": "done"}, where="name = 'run_42'")
    db.select("experiments", where="status = 'done'", limit=100)

    # Table management
    db.create_table(
        "results",
        {"id": "SERIAL PRIMARY KEY", "value": "DOUBLE PRECISION", "label": "TEXT"}
    )
    db.list_tables()

    # Batch operations
    db.batch_insert("experiments", [
        {"name": "run_1", "status": "done"},
        {"name": "run_2", "status": "pending"},
    ])
```

## Mixin Capabilities

`PostgreSQL` inherits these mixins (parallel structure to SQLite3):

| Mixin | Key methods |
|-------|-------------|
| `_ConnectionMixin` | `connect`, `close`, `execute` |
| `_QueryMixin` | `select`, `count`, `exists` |
| `_TransactionMixin` | `begin`, `commit`, `rollback` |
| `_TableMixin` | `create_table`, `drop_table`, `list_tables` |
| `_IndexMixin` | `create_index`, `drop_index` |
| `_RowMixin` | `insert`, `update`, `delete` |
| `_BatchMixin` | `batch_insert`, `batch_update` |
| `_BlobMixin` | `save_blob`, `load_blob` |
| `_ImportExportMixin` | `import_csv`, `export_csv` |
| `_MaintenanceMixin` | `vacuum`, `analyze` |
| `_SchemaMixin` | `describe`, `list_schemas` |
| `_BackupMixin` | `backup`, `restore` |

## Key Differences from SQLite3

- No `_ArrayMixin` (no compressed numpy BLOB storage)
- No `_GitMixin` (no git-based versioning)
- Has `_SchemaMixin` for schema-level operations
- Has `_BackupMixin` for pg_dump/restore operations
- Requires external PostgreSQL server and connection credentials
