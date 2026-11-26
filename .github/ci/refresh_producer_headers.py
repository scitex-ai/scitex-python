#!/usr/bin/env python3
"""Regenerate PRODUCER_HEADERS in test_release_identity.py from pyproject.toml.

The release-identity controls compare built archives against a frozen copy of
the core metadata headers that the pinned producer (Hatchling 1.30.1, see
build-in-sif.sh) emits for the public pyproject. Any change to the declared
requirements -- e.g. ``make sync-member-floors`` -- must refresh that copy, or
every release preflight refuses ("source runtime requirements differ").

Run with the pinned producer, from the repository root::

    uv run --no-project --with hatchling==1.30.1 \\
        python .github/ci/refresh_producer_headers.py           # rewrite
    ... refresh_producer_headers.py --check                    # exit 1 if stale
"""

from __future__ import annotations

import argparse
import base64
import re
import sys
import zlib
from pathlib import Path

PRODUCER = "1.30.1"
ROOT = Path(__file__).resolve().parents[2]
TEST_FILE = ROOT / ".github" / "ci" / "test_release_identity.py"
_BLOB_RE = re.compile(
    r"(PRODUCER_HEADERS = zlib\.decompress\(\n    base64\.b85decode\(\n)"
    r"(?P<lines>(?:        b\"[^\"]*\"\n)+)"
    r"(    \)\n\))"
)


def producer_headers(root: Path = ROOT) -> bytes:
    """Core metadata headers (README body excluded) from the pinned Hatchling."""
    from importlib.metadata import version

    from hatchling.metadata.core import ProjectMetadata
    from hatchling.metadata.spec import get_core_metadata_constructors

    if version("hatchling") != PRODUCER:
        raise SystemExit(f"need hatchling=={PRODUCER}, found {version('hatchling')}")
    metadata = ProjectMetadata(str(root), None)
    raw = get_core_metadata_constructors()["2.4"](metadata).encode()
    head, _, _body = raw.partition(b"\n\n")
    return head + b"\n"


def encode_lines(raw: bytes) -> str:
    encoded = base64.b85encode(zlib.compress(raw, 9)).decode()
    return "".join(
        f'        b"{encoded[i : i + 94]}"\n' for i in range(0, len(encoded), 94)
    )


def frozen_headers(text: str) -> bytes:
    match = _BLOB_RE.search(text)
    if match is None:
        raise SystemExit(f"PRODUCER_HEADERS literal not found in {TEST_FILE}")
    blob = "".join(re.findall(r'b"([^"]*)"', match["lines"]))
    return zlib.decompress(base64.b85decode(blob))


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--check", action="store_true", help="exit 1 if stale")
    args = parser.parse_args(argv)

    text = TEST_FILE.read_text()
    fresh = producer_headers()
    if frozen_headers(text) == fresh:
        print("OK: PRODUCER_HEADERS matches pyproject.toml")
        return 0
    if args.check:
        print("STALE: PRODUCER_HEADERS differs from pyproject.toml", file=sys.stderr)
        return 1
    updated = _BLOB_RE.sub(
        lambda m: m.group(1) + encode_lines(fresh) + m.group(3), text, count=1
    )
    TEST_FILE.write_text(updated)
    print(f"refreshed PRODUCER_HEADERS in {TEST_FILE}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
