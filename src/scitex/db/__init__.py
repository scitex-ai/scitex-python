#!/usr/bin/env python3
"""SciTeX Database — delegates to scitex-db."""

from scitex_db import (
    PostgreSQL,
    SQLite3,
    batch_health_check,
    check_health,
    delete_duplicates,
    delete_sqlite3_duplicates,
    inspect,
)

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
