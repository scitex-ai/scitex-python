---
name: stx.db
description: Database operations for PostgreSQL and SQLite3 with health checks and duplicate management.
---

# stx.db

The `stx.db` module provides database operation utilities for PostgreSQL and SQLite3. It offers high-level classes for database interaction, health checking, duplicate detection, and schema inspection.

## Python API

```python
import scitex as stx

# SQLite3
db = stx.db.SQLite3("experiments.db")
db.execute("CREATE TABLE IF NOT EXISTS results (id INTEGER PRIMARY KEY, value REAL)")
db.insert("results", {"value": 3.14})
rows = db.select("results", where="value > 3.0")

# PostgreSQL
db = stx.db.PostgreSQL(host="localhost", dbname="mydb", user="user")
db.execute("SELECT * FROM experiments LIMIT 10")

# Health checks
health = stx.db.check_health("experiments.db")
all_health = stx.db.batch_health_check(["db1.db", "db2.db"])

# Remove duplicates
stx.db.delete_duplicates(db, table="results", key_cols=["session_id"])
stx.db.delete_sqlite3_duplicates("experiments.db", table="results")

# Inspect schema
schema = stx.db.inspect("experiments.db")
```

## Key Features

- `SQLite3` — high-level SQLite3 database class
- `PostgreSQL` — high-level PostgreSQL database class
- `check_health` / `batch_health_check` — database connectivity and integrity checks
- `delete_duplicates` / `delete_sqlite3_duplicates` — duplicate row management
- `inspect` — schema inspection for any supported database
