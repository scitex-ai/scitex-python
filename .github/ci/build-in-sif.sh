#!/usr/bin/env bash
# Whole artifacts are built and imported in the existing qualified SIF Python.
set -euo pipefail
V="${1:-3.12}"
case "$V" in 3.11|3.12|3.13) ;; *) exit 1;; esac
PY="/opt/venv-$V/bin/python"
test -x "$PY"
: "${RELEASE_TAG:?}" "${RELEASE_COMMIT:?}" "${GITHUB_RUN_ID:?}" "${GITHUB_RUN_ATTEMPT:?}"
"$PY" -I -S -B .github/ci/release-identity.py check-source --tag "$RELEASE_TAG" --commit "$RELEASE_COMMIT"
export LC_ALL=C.UTF-8 LANG=C.UTF-8
TMPDIR="$(mktemp -d "/tmp/build-scitex-$GITHUB_RUN_ID-$GITHUB_RUN_ATTEMPT-$V-XXXXXX")"
export TMPDIR UV_CACHE_DIR="$TMPDIR/uv-cache" XDG_CACHE_HOME="$TMPDIR"
mkdir "$TMPDIR/site" "$TMPDIR/wheel-site"
unset VIRTUAL_ENV PYTHONHOME PYTHONPATH || true
export PATH="/opt/venv-$V/bin:$PATH"
command -v uv >/dev/null
# The reviewed project declares hatchling as its sole PEP517 backend. Install
# the complete frontend/backend normally into an exclusive target, then build
# from the sdist without creating another virtual environment.
"$PY" -c 'import tomllib; x=tomllib.load(open("pyproject.toml","rb")); assert x["build-system"] == {"requires":["hatchling"],"build-backend":"hatchling.build"}'
uv pip install --python "$PY" --target="$TMPDIR/site" build hatchling
export PYTHONPATH="$TMPDIR/site"
[ ! -e dist ] && [ ! -L dist ] || { echo "::error::stale release output refused"; exit 1; }
"$PY" -m build --no-isolation --outdir dist
WHEELS=(dist/*.whl)
[ "${#WHEELS[@]}" -eq 1 ] && [ -f "${WHEELS[0]}" ]
# Resolve the actual wheel's full runtime dependencies into a fresh target.
# -I -S keeps both the source checkout and baked site-packages out of imports.
uv pip install --python "$PY" --target="$TMPDIR/wheel-site" "${WHEELS[0]}"
"$PY" -I -S - "$TMPDIR/wheel-site" <<'PY'
from pathlib import Path
import importlib
import sys
site=Path(sys.argv[1]).resolve()
sys.path.insert(0,str(site))
umbrella = importlib.import_module("scitex")
cli = importlib.import_module("scitex.cli")
assert Path(umbrella.__file__).resolve().is_relative_to(site)
assert Path(cli.__file__).resolve().is_relative_to(site)
assert umbrella.__version__ == __import__("os").environ["RELEASE_TAG"][1:]
print("Actual isolated whole-wheel umbrella and CLI origins passed")
PY
"$PY" -I -S -B .github/ci/release-identity.py write-proof --tag "$RELEASE_TAG" --commit "$RELEASE_COMMIT"
