"""Read-only wait evidence for explicitly enabled disposable-database CI."""

from __future__ import annotations

import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import time


def observe(dsn: str) -> None:
    """Emit wait metadata, never SQL text, parameters or connection identity."""
    import psycopg
    from psycopg.rows import dict_row

    try:
        with psycopg.connect(
            dsn, autocommit=True, connect_timeout=2, row_factory=dict_row,
            application_name="scitex-pg-wait-observer",
        ) as connection:
            print(json.dumps({"ready": True}), flush=True)
            while True:
                activity = connection.execute("""
                    SELECT pid, state, wait_event_type, wait_event,
                           pg_blocking_pids(pid) AS blockers,
                           CASE
                             WHEN query ~* '^\\s*CREATE\\s+INDEX' THEN 'CREATE INDEX'
                             WHEN query ~* '^\\s*CREATE\\s+TABLE' THEN 'CREATE TABLE'
                             WHEN query ~* '^\\s*ALTER\\s+TABLE' THEN 'ALTER TABLE'
                             WHEN query ~* '^\\s*SELECT' THEN 'SELECT'
                             ELSE 'other'
                           END AS command_kind
                    FROM pg_stat_activity
                    WHERE datname = current_database() AND pid <> pg_backend_pid()
                      AND (wait_event_type IN ('Lock', 'IO')
                           OR state = 'idle in transaction')
                    ORDER BY pid
                """).fetchall()
                if activity:
                    pids = sorted({pid for row in activity
                                   for pid in [row["pid"], *row["blockers"]]})
                    locks = connection.execute("""
                        SELECT l.pid, n.nspname AS schema, c.relname AS relation,
                               l.locktype, l.mode, l.granted
                        FROM pg_locks l
                        LEFT JOIN pg_class c ON c.oid = l.relation
                        LEFT JOIN pg_namespace n ON n.oid = c.relnamespace
                        WHERE l.pid = ANY(%s)
                        ORDER BY l.pid, c.relname, l.mode
                    """, (pids,)).fetchall()
                    print(json.dumps({"activity": activity, "locks": locks}), flush=True)
                time.sleep(0.5)
    except Exception as error:
        # Driver errors can embed credentials. Only the class may leave here.
        print(json.dumps({"error_type": type(error).__name__}), flush=True)
        raise SystemExit(1) from None


class PostgresWaitObserver:
    """One independent observer process; no test-worker or Store changes."""

    def __init__(self, dsn: str):
        self.directory = Path(tempfile.mkdtemp(prefix="scitex-pg-waits-"))
        self.directory.chmod(0o700)
        self.path = self.directory / "observations.jsonl"
        descriptor = os.open(self.path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        with os.fdopen(descriptor, "wb") as output:
            self.process = subprocess.Popen(
                [sys.executable, "-I", "-B", str(Path(__file__).resolve())],
                stdin=subprocess.PIPE, stdout=output, stderr=subprocess.DEVNULL,
            )
        assert self.process.stdin is not None
        self.process.stdin.write(json.dumps({"dsn": dsn}).encode())
        self.process.stdin.close()

    def records(self) -> list[dict]:
        return [json.loads(line) for line in self.path.read_text().splitlines()]

    def finish(self) -> dict:
        if self.process.poll() is None:
            self.process.terminate()
            try:
                self.process.wait(timeout=2)
            except subprocess.TimeoutExpired:
                self.process.kill()
                self.process.wait(timeout=2)
        records = self.records()
        # Repeated samples add counts, not unbounded copies to the job log.
        patterns = {}
        for record in records:
            if "activity" not in record:
                continue
            key = json.dumps(record, sort_keys=True)
            if key not in patterns:
                patterns[key] = {**record, "samples": 0}
            patterns[key]["samples"] += 1
        return {
            "ready": any(record.get("ready") for record in records),
            "error_types": [record["error_type"] for record in records
                            if "error_type" in record],
            "process_exit": self.process.returncode,
            "wait_patterns": list(patterns.values()),
            "raw_metadata_path": str(self.path),
            "scope": "Read-only disposable PostgreSQL waits; no SQL text or parameters",
        }


if __name__ == "__main__":
    observe(json.load(sys.stdin)["dsn"])
