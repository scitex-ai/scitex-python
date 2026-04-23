"""Smoke tests for `scitex.db.SQLite3` — umbrella-level CRUD + numpy-array BLOB.

The standalone scitex-db package has deeper tests; this file covers the
umbrella re-export contract end-to-end to catch regressions where the
re-export breaks before a downstream release.
"""

from __future__ import annotations

import numpy as np
import pytest

import scitex.db as db


@pytest.fixture
def sqlite(tmp_path):
    path = tmp_path / "test.db"
    with db.SQLite3(str(path)) as s:
        yield s


class TestConnection:
    def test_context_manager_opens_and_closes(self, tmp_path):
        path = tmp_path / "cm.db"
        with db.SQLite3(str(path)) as s:
            assert s.db_path == str(path) or str(s.db_path) == str(path)
            # Can execute
            s.execute("CREATE TABLE t (id INTEGER)")
            s.commit()
        # After close the file still exists on disk
        assert path.exists()


class TestCRUD:
    def test_create_insert_query_roundtrip(self, sqlite):
        sqlite.execute("CREATE TABLE points (x REAL, y REAL)")
        sqlite.executemany(
            "INSERT INTO points (x, y) VALUES (?, ?)",
            [(1.0, 2.0), (3.0, 4.0), (5.0, 6.0)],
        )
        sqlite.commit()

        rows = sqlite.execute("SELECT x, y FROM points ORDER BY x").fetchall()
        assert rows == [(1.0, 2.0), (3.0, 4.0), (5.0, 6.0)]

    def test_delete_where(self, sqlite):
        sqlite.execute("CREATE TABLE t (id INTEGER, name TEXT)")
        sqlite.executemany(
            "INSERT INTO t VALUES (?, ?)", [(1, "a"), (2, "b"), (3, "c")]
        )
        sqlite.commit()

        sqlite.delete_where("t", "id = 2")
        sqlite.commit()

        names = [r[0] for r in sqlite.execute("SELECT name FROM t").fetchall()]
        assert names == ["a", "c"]


class TestTableOps:
    def test_create_and_drop_table(self, sqlite):
        sqlite.create_table("users", {"id": "INTEGER", "name": "TEXT"})
        # Table exists
        rows = sqlite.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='users'"
        ).fetchall()
        assert rows == [("users",)]

        sqlite.drop_table("users")
        rows = sqlite.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='users'"
        ).fetchall()
        assert rows == []

    def test_add_and_check_column(self, sqlite):
        sqlite.execute("CREATE TABLE t (id INTEGER)")
        assert not sqlite.column_exists("t", "extra")
        sqlite.add_column("t", "extra", "TEXT")
        assert sqlite.column_exists("t", "extra")


class TestArrayBlob:
    def test_numpy_roundtrip(self, sqlite):
        # The SciTeX-specific feature: numpy arrays stored as BLOBs.
        arr = np.array([[1.5, 2.5], [3.5, 4.5]], dtype=np.float64)

        sqlite.execute("CREATE TABLE arrays (name TEXT, data BLOB)")
        sqlite.execute(
            "INSERT INTO arrays (name, data) VALUES (?, ?)",
            ("x", arr.tobytes()),
        )
        sqlite.commit()

        blob = sqlite.execute("SELECT data FROM arrays WHERE name = 'x'").fetchone()[0]
        recovered = np.frombuffer(blob, dtype=np.float64).reshape(arr.shape)
        assert np.array_equal(arr, recovered)


# EOF
