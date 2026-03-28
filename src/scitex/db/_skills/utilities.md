---
description: Inspect database structure with inspect(), remove duplicate rows with delete_duplicates(), and run health checks with check_health() and batch_health_check().
---

# Database Utilities

## inspect

Return a structural summary of a database (tables, columns, row counts).

```python
stx.db.inspect(db_path: str) -> dict
```

```python
import scitex as stx

info = stx.db.inspect("experiment.db")
print(info)
# {'tables': {'results': {'columns': [...], 'row_count': 412}}}
```

---

## delete_duplicates

Remove duplicate rows from a table, keeping one copy.

```python
stx.db.delete_duplicates(db, table: str, subset: list[str] | None = None) -> int
```

Returns the number of rows deleted.

```python
import scitex as stx

db = stx.db.SQLite3("experiment.db")
n_deleted = stx.db.delete_duplicates(db, "results", subset=["score", "label"])
print(f"Removed {n_deleted} duplicates")
```

SQLite3-specific variant:

```python
stx.db.delete_sqlite3_duplicates(db_path: str, table: str) -> int
```

---

## check_health

Run a health check on a database connection, returning a status dict.

```python
stx.db.check_health(db) -> dict
```

```python
import scitex as stx

db = stx.db.PostgreSQL(...)
health = stx.db.check_health(db)
print(health)
# {'connected': True, 'tables': 5, 'errors': []}
```

---

## batch_health_check

Check multiple databases at once.

```python
stx.db.batch_health_check(db_list: list) -> list[dict]
```
