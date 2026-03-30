#!/usr/bin/env python3
"""SciTeX Database -- delegates to scitex-db package."""

try:
    from scitex_db import (
        PostgreSQL,
        SQLite3,
        batch_health_check,
        check_health,
        delete_duplicates,
        delete_sqlite3_duplicates,
        inspect,
    )

    _BACKEND = "scitex-db"
except ImportError:
    from ._check_health import batch_health_check, check_health
    from ._delete_duplicates import delete_duplicates
    from ._inspect import inspect
    from ._postgresql._PostgreSQL import PostgreSQL
    from ._sqlite3._delete_duplicates import delete_sqlite3_duplicates
    from ._sqlite3._SQLite3 import SQLite3

    _BACKEND = "local"

__all__ = [
    "PostgreSQL",
    "SQLite3",
    "batch_health_check",
    "check_health",
    "delete_duplicates",
    "delete_sqlite3_duplicates",
    "inspect",
]

# EOF
