"""Keep collection, fixtures and child processes off the live fleet store.

Loaded with ``-p`` before collection. CI supplies a disposable PostgreSQL via
SCITEX_STORE_DSN; local database tests may opt in with SCITEX_TEST_PG_DSN.
Never include a DSN in errors: it may contain a password.
"""

from __future__ import annotations

import os
import re
from urllib.parse import parse_qs, unquote, urlsplit

import pytest

_FLEET_HOSTS = {
    "scitex-primary",
    "cards-primary",
    "scitex-nas-03",
    *(f"scitex-compute-0{i}" for i in range(1, 5)),
    *(f"100.64.0.{i}" for i in range(1, 6)),
}
_FLEET_PORTS = {"55432", "55433"}
_UNREACHABLE = "postgresql://scitex_tests@127.0.0.1:1/no_test_database_configured"


def fleet_endpoint(dsn: str) -> bool:
    """Recognize URI, socket, multi-host and keyword libpq fleet targets."""
    values: dict[str, list[str]] = {}
    if "://" in dsn:
        parts = urlsplit(dsn)
        values = parse_qs(parts.query)
        for endpoint in parts.netloc.rpartition("@")[2].split(","):
            if endpoint.startswith("["):
                host, _, port = endpoint[1:].partition("]")
                port = port.lstrip(":")
            else:
                host, _, port = endpoint.partition(":")
            values.setdefault("host", []).append(unquote(host))
            values.setdefault("port", []).append(port)
    else:
        for key, raw in re.findall(r"(\w+)\s*=\s*('(?:[^'\\]|\\.)*'|\S+)", dsn):
            values.setdefault(key, []).append(raw.strip("'"))
    hosts = values.get("host", []) + values.get("hostaddr", [])
    return any(
        host.strip().lower().rstrip(".") in _FLEET_HOSTS
        for value in hosts
        for host in value.split(",")
    ) or any(
        port.strip() in _FLEET_PORTS
        for value in values.get("port", [])
        for port in value.split(",")
    )


def isolated_environment(environ: dict[str, str]) -> dict[str, str]:
    """Select an explicit test target and discard inherited libpq identity."""
    declared = environ.get("SCITEX_TEST_PG_DSN", "")
    inherited = environ.get("SCITEX_STORE_DSN", "")
    if declared and fleet_endpoint(declared):
        raise pytest.UsageError("SCITEX_TEST_PG_DSN names the live fleet database")
    # The shared CI workflow exports its disposable service here. An inherited
    # fleet target from an interactive shell must never become a test target.
    target = declared or (
        inherited if inherited and not fleet_endpoint(inherited) else _UNREACHABLE
    )
    result = {key: value for key, value in environ.items() if not key.startswith("PG")}
    result.update(
        SCITEX_STORE_DSN=target,
        SCITEX_CARDS_DB=target,
        PGHOST="127.0.0.1",
        PGPORT="1",
        PGUSER="scitex_tests_have_no_fleet_identity",
        PGPASSFILE=os.devnull,
        PGSERVICEFILE=os.devnull,
        PGSYSCONFDIR=os.devnull,
        PGCONNECT_TIMEOUT="2",
    )
    return result


_isolated = isolated_environment(dict(os.environ))
for _key in tuple(os.environ):
    if _key.startswith("PG"):
        del os.environ[_key]
os.environ.update(_isolated)


@pytest.fixture(autouse=True)
def _no_fleet_database_environment():
    """Reassert isolation per test and report a leaked fleet target."""
    saved = dict(os.environ)
    try:
        yield
    finally:
        leaked = any(
            fleet_endpoint(os.environ.get(key, ""))
            for key in ("SCITEX_STORE_DSN", "SCITEX_CARDS_DB")
        ) or fleet_endpoint(
            f"host={os.environ.get('PGHOST', '')} "
            f"hostaddr={os.environ.get('PGHOSTADDR', '')} "
            f"port={os.environ.get('PGPORT', '')}"
        )
        for key in tuple(os.environ):
            if key.startswith("PG") or key in ("SCITEX_STORE_DSN", "SCITEX_CARDS_DB"):
                os.environ.pop(key, None)
        os.environ.update(
            {
                key: value
                for key, value in saved.items()
                if key.startswith("PG")
                or key in ("SCITEX_STORE_DSN", "SCITEX_CARDS_DB")
            }
        )
        if leaked:
            pytest.fail("Test left a live fleet database target in its environment")
