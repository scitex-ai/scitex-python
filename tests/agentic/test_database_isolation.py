"""Exercise the real pytest startup and child-process environment boundary."""

import json
import os
import subprocess
import sys
from pathlib import Path

import pytest
from _database_isolation import fleet_endpoint, isolated_environment


@pytest.mark.parametrize(
    "dsn",
    [
        "postgresql://scitex-primary/scitex",
        "postgres://cards-primary/scitex",
        "postgresql://SCITEX-PRIMARY./scitex",
        "postgresql://100.64.0.5/scitex",
        "postgresql://scitex-compute-02/scitex",
        "postgresql://127.0.0.1:55432/scitex",
        "postgresql://[::1]:55433/scitex",
        "postgresql://localhost/scitex?host=scitex-primary",
        "postgresql://localhost/scitex?hostaddr=100.64.0.5",
        "postgresql://localhost/scitex?host=/tmp&port=55432",
        "postgresql://localhost:5432,scitex-primary:5432/scitex",
        "host='localhost,scitex-primary' dbname=scitex",
        "hostaddr=100.64.0.5 dbname=scitex",
        "host='/tmp' port='55433' dbname=scitex",
    ],
)
def test_explicit_fleet_target_is_refused_without_disclosing_credentials(dsn):
    assert fleet_endpoint(dsn)
    with pytest.raises(pytest.UsageError) as error:
        isolated_environment({"SCITEX_TEST_PG_DSN": dsn})
    assert "private" not in str(error.value)


def test_runner_credentials_are_discarded_and_children_inherit_isolation():
    runner = dict(os.environ)
    runner.update(
        SCITEX_STORE_DSN="postgresql://scitex-primary:55432/scitex",
        SCITEX_CARDS_DB="postgresql://scitex-primary:55432/scitex",
        PGPASSWORD="runner-secret",
        PGUSER="real-role",
        PGHOSTADDR="100.64.0.5",
        PGSERVICE="production",
        PGPASSFILE="/runner/home/.pgpass",
    )
    runner.pop("SCITEX_TEST_PG_DSN", None)
    child = subprocess.run(
        [sys.executable, "-c", "import json,os; print(json.dumps(dict(os.environ)))"],
        env=isolated_environment(runner),
        capture_output=True,
        text=True,
        check=True,
    )
    actual = json.loads(child.stdout)
    assert actual["PGPASSFILE"] == os.devnull
    assert actual["PGUSER"] == "scitex_tests_have_no_fleet_identity"
    assert actual["PGPORT"] == "1"
    assert actual["SCITEX_STORE_DSN"] == actual["SCITEX_CARDS_DB"]
    assert ":1/" in actual["SCITEX_STORE_DSN"]
    assert not {"PGPASSWORD", "PGHOSTADDR", "PGSERVICE"} & actual.keys()


def test_disposable_ci_database_is_preserved():
    target = "postgresql://scitex:scitex@127.0.0.1:45431/scitex"
    actual = isolated_environment({"SCITEX_STORE_DSN": target})
    assert actual["SCITEX_STORE_DSN"] == target
    assert actual["SCITEX_CARDS_DB"] == target


def test_disposable_database_accepts_real_queries():
    target = os.environ["SCITEX_STORE_DSN"]
    if "no_test_database_configured" in target:
        pytest.skip("No disposable PostgreSQL configured")
    psycopg = pytest.importorskip("psycopg")
    with psycopg.connect(target) as conn:
        conn.execute("CREATE TEMP TABLE isolation_probe (value integer)")
        conn.execute("INSERT INTO isolation_probe VALUES (42)")
        assert conn.execute("SELECT value FROM isolation_probe").fetchone() == (42,)


def _pytest_child(tmp_path, source, extra_env):
    probe = tmp_path / "test_probe.py"
    probe.write_text(source)
    root = Path(__file__).resolve().parents[2]
    env = dict(os.environ, PYTEST_DISABLE_PLUGIN_AUTOLOAD="1", **extra_env)
    return subprocess.run(
        [
            sys.executable,
            "-m",
            "pytest",
            "-c",
            str(root / "pyproject.toml"),
            "-o",
            "addopts=-p _database_isolation",
            "-q",
            str(probe),
        ],
        env=env,
        cwd=root,
        capture_output=True,
        text=True,
        timeout=30,
    )


def test_isolation_precedes_collection(tmp_path):
    result = _pytest_child(
        tmp_path,
        """
import os
assert os.environ["PGPASSFILE"] == os.devnull
assert os.environ["PGPORT"] == "1"
assert "PGPASSWORD" not in os.environ
def test_probe():
    pass
""",
        {
            "SCITEX_STORE_DSN": "postgresql://scitex-primary:55432/scitex",
            "PGPASSWORD": "runner-secret",
        },
    )
    assert result.returncode == 0, result.stdout + result.stderr


def test_explicit_fleet_target_fails_before_collection(tmp_path):
    result = _pytest_child(
        tmp_path,
        "raise RuntimeError('COLLECTED')\n",
        {
            "SCITEX_TEST_PG_DSN": "postgresql://user:private@scitex-primary/scitex",
        },
    )
    assert result.returncode != 0
    assert "live fleet database" in result.stderr
    assert "private" not in result.stderr
    assert "COLLECTED" not in result.stdout + result.stderr


def test_test_leaking_fleet_target_fails(tmp_path):
    result = _pytest_child(
        tmp_path,
        """
import os
def test_probe():
    os.environ["SCITEX_STORE_DSN"] = "postgresql://scitex-primary/scitex"
""",
        {},
    )
    assert result.returncode != 0
    assert "left a live fleet database target" in result.stdout
