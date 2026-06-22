#!/usr/bin/env bash
# Runs INSIDE the reused scitex-ci SIF (apptainer exec — invoked via
# exec-in-sif.sh). Publishes ./dist/* to PyPI via MANUAL OIDC Trusted
# Publishing, then twine upload.
#
# WHY manual OIDC (not pypa/gh-action-pypi-publish): that action is a Docker
# container action. Self-hosted Spartan compute nodes have NO Docker, so the
# action cannot run there. PyPI Trusted Publishing is just an OIDC token
# exchange over plain HTTPS, so we do it by hand:
#
#   1. Ask the GitHub Actions OIDC provider for a JWT with audience=pypi,
#      using the per-job ACTIONS_ID_TOKEN_REQUEST_{TOKEN,URL} env vars (present
#      because the publish job declares `permissions: id-token: write`).
#      apptainer exec (no --cleanenv) passes those host env vars into the SIF.
#   2. Exchange that JWT at PyPI's mint-token endpoint for a short-lived,
#      scope-limited PyPI API token.
#   3. twine upload dist/* with TWINE_USERNAME=__token__ and that minted token.
#
# This requires a Trusted Publisher to be configured on PyPI for
# (project=scitex, owner=ywatanabe1989, repo=scitex-python,
#  workflow=pypi-publish-and-github-release-on-tag.yml). It already is — the
# previous releases published via the Docker action under the same trusted
# publisher; only the *client* changes here, not PyPI's trust config.
#
# curl, python and (after a --target install) twine all live in the SIF.
#
# Fail-loud (operator directive): every step asserts non-empty output and
# `set -euo pipefail`; any failure is a HARD error with the exact cause, never
# a silent skip.
set -euo pipefail

V="${1:-3.12}"
VENV="/opt/venv-$V"
PY="$VENV/bin/python"
test -x "$PY" || {
    echo "::error::baked python missing in $VENV — rebuild the SIF: scitex-container apptainer build ci-cpu"
    exit 1
}

export LC_ALL=C.UTF-8 LANG=C.UTF-8

# dist/ must already hold the artifacts (downloaded by the publish job before
# this script runs). Fail loud if empty.
if [ ! -d dist ] || [ -z "$(ls -A dist 2>/dev/null)" ]; then
    echo "::error::dist/ is empty — nothing to publish (download the build artifact first)"
    exit 1
fi
echo "=== dist to publish ==="
ls -l dist

# --- writable scratch (compute-node HOME is RO inside the container) ---
TMPDIR="/tmp/publish-scitex-${GITHUB_RUN_ID:-0}-${GITHUB_RUN_ATTEMPT:-0}-$V"
export TMPDIR
rm -rf "$TMPDIR"
mkdir -p "$TMPDIR/site" "$TMPDIR/uv-cache"
export UV_CACHE_DIR="$TMPDIR/uv-cache"
export XDG_CACHE_HOME="$TMPDIR"
export PIP_CACHE_DIR="$TMPDIR/pip-cache"
unset VIRTUAL_ENV || true
export PATH="$VENV/bin:$PATH"

# --- step 1: request the OIDC JWT (audience=pypi) from GitHub ---
: "${ACTIONS_ID_TOKEN_REQUEST_TOKEN:?ACTIONS_ID_TOKEN_REQUEST_TOKEN not set — the publish job needs 'permissions: id-token: write'}"
: "${ACTIONS_ID_TOKEN_REQUEST_URL:?ACTIONS_ID_TOKEN_REQUEST_URL not set — the publish job needs 'permissions: id-token: write'}"

echo "=== minting OIDC JWT (audience=pypi) ==="
JWT="$(curl -fsS \
    -H "Authorization: bearer ${ACTIONS_ID_TOKEN_REQUEST_TOKEN}" \
    "${ACTIONS_ID_TOKEN_REQUEST_URL}&audience=pypi" |
    "$PY" -c 'import sys,json; print(json.load(sys.stdin)["value"])')"
test -n "$JWT" || {
    echo "::error::OIDC JWT request returned an empty token"
    exit 1
}
echo "OIDC JWT obtained (length=${#JWT})"

# --- step 2: exchange the JWT for a short-lived PyPI API token ---
echo "=== exchanging JWT at PyPI mint-token endpoint ==="
MINT_RESP="$(curl -sS -X POST https://pypi.org/_/oidc/mint-token \
    -d "{\"token\":\"${JWT}\"}")"
MINTED="$(printf '%s' "$MINT_RESP" |
    "$PY" -c 'import sys,json; d=json.load(sys.stdin); print(d.get("token",""))')"
if [ -z "$MINTED" ]; then
    # Surface PyPI's error body VERBATIM (the JWT is NOT echoed) so a trust
    # misconfiguration is diagnosable — this is the decisive failure mode for
    # the fleet. Print the raw response unconditionally (most reliable on an
    # error path); pretty-print is best-effort on top.
    echo "::error::PyPI mint-token returned no token."
    echo "--- PyPI mint-token response body (raw) ---"
    printf '%s\n' "$MINT_RESP"
    echo "--- (pretty, best-effort) ---"
    printf '%s' "$MINT_RESP" |
        "$PY" -c 'import sys,json; print(json.dumps(json.load(sys.stdin), indent=2))' \
            2>/dev/null || true
    exit 1
fi
echo "PyPI token minted (length=${#MINTED})"

# --- step 3: install twine into the writable target, then upload ---
echo "=== installing twine (--target) ==="
uv pip install --python "$PY" --target="$TMPDIR/site" twine ||
    "$PY" -m pip install --target="$TMPDIR/site" twine
export PYTHONPATH="$TMPDIR/site${PYTHONPATH:+:$PYTHONPATH}"

echo "=== twine upload dist/* ==="
TWINE_USERNAME="__token__" TWINE_PASSWORD="$MINTED" \
    "$PY" -m twine upload --non-interactive --disable-progress-bar dist/*

echo "PUBLISH-OK: scitex dist/* uploaded to PyPI via manual OIDC trusted publishing"
