---
name: stx.db
description: Database operations for PostgreSQL and SQLite3 with numpy array storage, health checks, and duplicate management.
---

# stx.db

The `stx.db` module provides high-level database operation classes for PostgreSQL and SQLite3 with shared mixin architecture, health checking, duplicate detection, and schema inspection.

## Sub-skills

- [sqlite3-usage.md](sqlite3-usage.md) — `SQLite3` class, numpy array storage, mixin capabilities, health checks, duplicate removal, schema inspection
- [postgresql-usage.md](postgresql-usage.md) — `PostgreSQL` class, connection, core operations, differences from SQLite3

## Quick Reference

```python
import scitex as stx

# SQLite3 (with automatic compression, numpy BLOB support)
with stx.db.SQLite3("experiments.db") as db:
    db.create_table("results", {"id": "INTEGER PRIMARY KEY", "value": "REAL"})
    db.insert("results", {"value": 3.14})
    rows = db.select("results", where="value > 3.0")
    db.save_array("results", np_array, column="data")

# PostgreSQL
with stx.db.PostgreSQL(host="localhost", dbname="mydb", user="user") as db:
    db.execute("SELECT * FROM experiments LIMIT 10")

# Health and maintenance
health = stx.db.check_health("experiments.db")
stx.db.delete_sqlite3_duplicates("experiments.db", table="results")
schema = stx.db.inspect("experiments.db")
```

## Exports

| Name | Description |
|------|-------------|
| `SQLite3` | High-level SQLite3 class with compression and numpy array support |
| `PostgreSQL` | High-level PostgreSQL class |
| `check_health` | Check database health for one database |
| `batch_health_check` | Check health for multiple databases |
| `delete_duplicates` | Remove duplicate rows from any database |
| `delete_sqlite3_duplicates` | SQLite3-specific duplicate removal |
| `inspect` | Inspect database schema |
