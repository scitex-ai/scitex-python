#!/usr/bin/env python3
# File: ./tests/scitex/resource/test_import_no_side_effect.py

"""Regression tests for todo #157.

`from scitex.resource import get_specs` must be silent — no dashboard
server, no background thread, no listener on the canonical Flask port
(5000). Sidecars / CLI tools shell out via this import on every metrics
tick, so any spawned listener is a real bug.

References:
    https://github.com/ywatanabe1989/todo/issues/157
"""

from __future__ import annotations

import socket
import subprocess
import sys
import textwrap


def _is_listening(port: int, host: str = "127.0.0.1") -> bool:
    """Return True if *something* is currently listening on host:port."""
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(0.5)
    try:
        return s.connect_ex((host, port)) == 0
    finally:
        s.close()


def _run_isolated(script: str) -> subprocess.CompletedProcess:
    """Run *script* in a clean Python subprocess so test-time state can't
    pollute the assertion (e.g. a dashboard server already imported by a
    previous test, dev tooling, or the user's REPL).
    """
    return subprocess.run(
        [sys.executable, "-c", textwrap.dedent(script)],
        capture_output=True,
        text=True,
        timeout=60,
    )


def test_import_does_not_start_dashboard():
    """Importing scitex.resource must not spawn a listener on :5000.

    We compare listener-on-:5000 state before vs. after the import inside
    a fresh subprocess; the test passes when the import does not change
    that state from "not-listening" to "listening".
    """
    script = """
        import json, socket, sys, time

        def listening(port):
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(0.5)
            try:
                return s.connect_ex(("127.0.0.1", port)) == 0
            finally:
                s.close()

        before = listening(5000)
        from scitex.resource import get_specs  # the canonical sidecar entry point  # noqa: F401
        # Allow any (errant) background thread to bind before we sample.
        time.sleep(1.0)
        after = listening(5000)

        json.dump({"before": before, "after": after}, sys.stdout)
    """
    proc = _run_isolated(script)
    assert proc.returncode == 0, (
        f"subprocess crashed during import:\nSTDOUT:{proc.stdout}\nSTDERR:{proc.stderr}"
    )

    import json

    state = json.loads(proc.stdout)
    # If :5000 was already taken by something unrelated (CI runner, dev's
    # own dashboard) we cannot assert about post-import state — but we can
    # still assert the import did not flip the bit from free → bound.
    if not state["before"]:
        assert not state["after"], (
            "Importing scitex.resource started a listener on :5000 — "
            "see todo #157. Dashboard / server launches must be opt-in via "
            "an explicit start_dashboard() call or `python -m ...` entry."
        )


def test_import_does_not_pull_heavy_io_chain():
    """Importing scitex.resource must stay lightweight.

    The historical regression vector is the `_log_processor_usages` module
    pulling `scitex.io` → `scitex_io` → `scitex_dev` (which has, in past
    versions, pulled dashboard-bearing modules at import time). Keep this
    chain *out* of the eager import path.
    """
    script = """
        import json, sys

        before = set(sys.modules)
        from scitex.resource import get_specs  # noqa: F401
        new = set(sys.modules) - before

        offenders = sorted(
            m for m in new
            if m.startswith(("scitex.io", "scitex_io", "scitex_dev"))
        )
        json.dump(offenders, sys.stdout)
    """
    proc = _run_isolated(script)
    assert proc.returncode == 0, (
        f"subprocess crashed during import:\nSTDOUT:{proc.stdout}\nSTDERR:{proc.stderr}"
    )

    import json

    offenders = json.loads(proc.stdout)
    assert offenders == [], (
        "Importing scitex.resource eagerly pulled in the scitex.io / "
        "scitex_dev chain, which has historically carried dashboard "
        "side effects (todo #157). Keep log_processor_usages lazy. "
        f"Offending modules: {offenders}"
    )


def test_log_processor_usages_still_accessible_lazily():
    """Lazy attribute access must still resolve `log_processor_usages`."""
    import scitex.resource as resource

    fn = resource.log_processor_usages  # triggers lazy import
    assert callable(fn)
    # `main` is the alias used by ``python -m scitex.resource``-style entry.
    assert callable(resource.main)


# EOF
