#!/usr/bin/env bash
# Same manual OIDC trusted publisher, after source/tag/artifact qualification.
set -euo pipefail
V="${1:-3.12}"
case "$V" in 3.11|3.12|3.13) ;; *) exit 1;; esac
PY="/opt/venv-$V/bin/python"
test -x "$PY"
: "${RELEASE_TAG:?}" "${RELEASE_COMMIT:?}" "${GITHUB_RUN_ID:?}" "${GITHUB_RUN_ATTEMPT:?}"
export LC_ALL=C.UTF-8 LANG=C.UTF-8
unset VIRTUAL_ENV PYTHONHOME PYTHONPATH || true
export PATH="/opt/venv-$V/bin:$PATH"
command -v uv >/dev/null
# No credential exchange is attempted before this full immutable-artifact gate.
"$PY" -I -S -B .github/ci/release-identity.py verify-proof --tag "$RELEASE_TAG" --commit "$RELEASE_COMMIT" --revalidate
DIST=(dist/*.whl dist/*.tar.gz)
[ "${#DIST[@]}" -eq 2 ]
TMPDIR="$(mktemp -d "/tmp/publish-scitex-$GITHUB_RUN_ID-$GITHUB_RUN_ATTEMPT-$V-XXXXXX")"
export TMPDIR UV_CACHE_DIR="$TMPDIR/uv-cache" XDG_CACHE_HOME="$TMPDIR"
mkdir "$TMPDIR/site"
uv pip install --python "$PY" --target="$TMPDIR/site" twine
export PYTHONPATH="$TMPDIR/site"
: "${ACTIONS_ID_TOKEN_REQUEST_TOKEN:?}" "${ACTIONS_ID_TOKEN_REQUEST_URL:?}"
# The token stays out of argv and error bodies. Trust continues to use the
# same repository/workflow/pypi environment; there is no account fallback.
MINTED="$("$PY" - <<'PY'
import json,os,urllib.request
request=urllib.request.Request(os.environ["ACTIONS_ID_TOKEN_REQUEST_URL"]+"&audience=pypi",headers={"Authorization":"bearer "+os.environ["ACTIONS_ID_TOKEN_REQUEST_TOKEN"]})
with urllib.request.urlopen(request,timeout=30) as response:
 token=json.load(response)["value"]
request=urllib.request.Request("https://pypi.org/_/oidc/mint-token",data=json.dumps({"token":token}).encode(),headers={"Content-Type":"application/json"},method="POST")
with urllib.request.urlopen(request,timeout=30) as response:
 minted=json.load(response)["token"]
assert isinstance(minted,str) and minted
print(minted)
PY
)"
test -n "$MINTED"
# Recheck bytes immediately before the upload; the network membership/tag
# check already completed before OIDC, and was not replaced by quota fallback.
"$PY" -I -S -B .github/ci/release-identity.py verify-proof --tag "$RELEASE_TAG" --commit "$RELEASE_COMMIT"
TWINE_USERNAME=__token__ TWINE_PASSWORD="$MINTED" "$PY" -m twine upload --non-interactive --disable-progress-bar "${DIST[@]}"
unset MINTED
echo "PUBLISH-OK: verified scitex wheel and sdist uploaded"
