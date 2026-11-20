"""Exercise real observer processes and PostgreSQL locks without SQL disclosure."""

import os
import threading
import time
import uuid

import pytest

from _postgres_waits import PostgresWaitObserver


def test_connection_failure_records_only_the_error_class():
    # Arrange: this is an actual refused local connection, with a fake canary.
    secret = "wait-observer-password-canary"
    observer = PostgresWaitObserver(
        f"postgresql://diagnostic:{secret}@127.0.0.1:1/absent"
    )
    # Act
    observer.process.wait(timeout=10)
    report = observer.finish()
    # Assert
    raw = observer.path.read_text()
    assert report["ready"] is False
    assert report["error_types"] == ["OperationalError"]
    assert report["process_exit"] == 1
    assert secret not in raw
    assert "postgresql://" not in raw
    assert observer.path.stat().st_mode & 0o777 == 0o600
    assert observer.directory.stat().st_mode & 0o777 == 0o700


def test_real_blocker_is_captured_without_query_text_or_parameters():
    # Arrange: only the already isolated test target is eligible.
    target = os.environ["SCITEX_STORE_DSN"]
    if "no_test_database_configured" in target:
        pytest.skip("No disposable PostgreSQL configured")
    import psycopg
    from psycopg import sql

    name = "wait_probe_" + uuid.uuid4().hex
    canary = "wait-observer-SQL-literal-canary"
    observer = PostgresWaitObserver(target)
    blocker = psycopg.connect(target)
    waiter = psycopg.connect(target, autocommit=True)
    admin = psycopg.connect(target, autocommit=True)
    errors = []
    thread = None
    try:
        admin.execute(sql.SQL("CREATE TABLE {} (value text)").format(sql.Identifier(name)))
        blocker.execute(sql.SQL("LOCK TABLE {} IN ACCESS EXCLUSIVE MODE").format(
            sql.Identifier(name)
        ))
        blocker_pid, waiter_pid = blocker.info.backend_pid, waiter.info.backend_pid

        def wait_on_table():
            try:
                # A real literal is visible in pg_stat_activity; the observer
                # must emit only the fixed command classification, not it.
                waiter.execute(sql.SQL("SELECT {} FROM {}").format(
                    sql.Literal(canary), sql.Identifier(name)
                )).fetchall()
            except Exception as error:
                errors.append(type(error).__name__)

        # Act
        thread = threading.Thread(target=wait_on_table)
        thread.start()
        deadline = time.monotonic() + 5
        found = False
        while time.monotonic() < deadline:
            records = observer.records()
            found = any(
                row["pid"] == waiter_pid and blocker_pid in row["blockers"]
                and row["wait_event_type"] == "Lock"
                and row["command_kind"] == "SELECT"
                for record in records for row in record.get("activity", [])
            )
            if found:
                break
            time.sleep(0.05)
        blocker.rollback()
        thread.join(timeout=5)
        report = observer.finish()
        # Assert
        raw = observer.path.read_text()
        assert found, report
        assert not thread.is_alive() and not errors
        assert report["ready"] and not report["error_types"]
        assert any(
            lock["relation"] == name and lock["granted"] is False
            for pattern in report["wait_patterns"] for lock in pattern["locks"]
        )
        assert canary not in raw
        assert "postgresql://" not in raw
    finally:
        blocker.rollback()
        if thread is not None:
            thread.join(timeout=5)
        observer.finish()
        waiter.close()
        blocker.close()
        admin.execute(sql.SQL("DROP TABLE IF EXISTS {}").format(sql.Identifier(name)))
        admin.close()
