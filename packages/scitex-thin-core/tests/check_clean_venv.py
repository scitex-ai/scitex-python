"""Clean-venv assertions for the thin scitex core prototype.

Run by ``run_proof.sh`` inside each matrix venv:

    python -I check_clean_venv.py <comma-separated expected names | ->

Prints one PASS/FAIL line per check; exits non-zero on any FAIL.
(Deliberately no @stx.session: the venvs under test hold only the thin core
and the leaves being proven.)
"""

import importlib.metadata as md
import os
import subprocess
import sys
import tempfile
import time

_PROBE = "import sys, scitex; print('importlib.metadata' in sys.modules)"


class _Checks:
    def __init__(self):
        self.fails = 0

    def __call__(self, label, cond, detail=""):
        self.fails += not cond
        mark = "PASS" if cond else "FAIL"
        print(f"{mark}  {label}" + (f"  [{detail}]" if detail else ""))


def _check_core(check, stx, expected, import_ms):
    print(
        f"scitex dist version: {md.version('scitex')}  (import scitex: {import_ms:.1f} ms)"
    )
    check(
        "scitex resolves to the thin core 3.0.0.dev0",
        md.version("scitex") == "3.0.0.dev0",
    )
    check(
        "import scitex loads no leaf",
        not any(m in sys.modules for m in ("scitex_io", "scitex_str")),
    )
    # Fresh interpreter: this checker itself imports importlib.metadata.
    probe = subprocess.run(
        [sys.executable, "-I", "-c", _PROBE],
        capture_output=True,
        text=True,
        check=False,
    )
    check(
        "import scitex (fresh interpreter) does not import importlib.metadata",
        probe.stdout.strip() == "False",
        probe.stdout.strip() or probe.stderr.strip()[-200:],
    )
    check("stx.__version__ == 3.0.0.dev0", stx.__version__ == "3.0.0.dev0")
    mods = stx.list_modules()
    print("list_modules():", mods)
    check(
        "registered names == expected",
        sorted(mods) == sorted(expected),
        f"{sorted(mods)}",
    )


def _check_io_present(check, stx):
    import numpy as np
    import scitex_io

    check("stx.io is scitex_io (same object, no proxy)", stx.io is scitex_io)
    with tempfile.TemporaryDirectory(dir=os.environ.get("PROOF_SCRATCH")) as d:
        p = os.path.join(d, "x.json")
        stx.io.save({"a": 1, "b": [1, 2]}, p, verbose=False)
        back = stx.io.load(p)
        check(
            "stx.io.save/load round-trip (json)",
            back == {"a": 1, "b": [1, 2]},
            repr(back),
        )
        q = os.path.join(d, "x.npy")
        stx.io.save(np.arange(5), q, verbose=False)
        check(
            "stx.io.save/load round-trip (npy)",
            bool((stx.io.load(q) == np.arange(5)).all()),
        )
    from scitex.io import load

    check("from scitex.io import load", load is scitex_io.load)
    import scitex.io as sio

    check("import scitex.io as sio -> scitex_io", sio is scitex_io)
    check(
        "scitex_io.__spec__ not clobbered by alias import",
        scitex_io.__spec__.name == "scitex_io",
        scitex_io.__spec__.name,
    )


def _check_io_absent(check, stx):
    try:
        stx.io
        check("stx.io without scitex-io raises", False)
    except AttributeError as e:
        check(
            "stx.io without scitex-io -> AttributeError naming scitex-io",
            "pip install scitex-io" in str(e),
            str(e),
        )
    check("hasattr(stx, 'io') is False", not hasattr(stx, "io"))
    try:
        from scitex import io  # noqa: F401

        check("from scitex import io without scitex-io raises", False)
    except ImportError as e:
        check(
            "from scitex import io -> ImportError naming scitex-io",
            "scitex-io" in str(e),
            str(e),
        )


def _check_str(check, stx, present):
    if present:
        import scitex_str

        check("stx.str is scitex_str", stx.str is scitex_str)
        check("stx.str.squeeze_spaces works", stx.str.squeeze_spaces("a   b") == "a b")
        return
    import importlib.util

    how = (
        "installed from PyPI WITHOUT the entry point (version skew)"
        if importlib.util.find_spec("scitex_str")
        else "not installed"
    )
    try:
        stx.str
        check(f"stx.str with scitex-str {how} raises", False)
    except AttributeError as e:
        check(
            f"stx.str with scitex-str {how} -> names scitex-str",
            "pip install scitex-str" in str(e),
            str(e),
        )


def _check_override_hint(check, stx):
    try:
        stx.plt
        check("stx.plt (figrecipe absent) raises", False)
    except AttributeError as e:
        check(
            "stx.plt hint names figrecipe (override table)",
            "pip install figrecipe" in str(e),
            str(e),
        )


def main(argv):
    expected = [] if argv[1] == "-" else argv[1].split(",")
    check = _Checks()
    t0 = time.perf_counter()
    import scitex as stx

    import_ms = (time.perf_counter() - t0) * 1_000
    _check_core(check, stx, expected, import_ms)
    if "io" in expected:
        _check_io_present(check, stx)
    else:
        _check_io_absent(check, stx)
    _check_str(check, stx, "str" in expected)
    _check_override_hint(check, stx)
    print("RESULT:", "ALL PASS" if not check.fails else f"{check.fails} FAIL")
    return 1 if check.fails else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
