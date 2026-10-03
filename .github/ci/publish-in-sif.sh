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
SCRATCH_PREFIX="/tmp/publish-scitex-$GITHUB_RUN_ID-$GITHUB_RUN_ATTEMPT-$V-"

# BEGIN owned temporary-root lifecycle
OWNED_TMPDIR=""
OWNED_TMP_ID=""
OWNED_CHILD_PID=""
OWNED_CHILD_GROUP=""
OWNED_CHILD_BIRTH=""

owned_birth() {
    local line
    IFS= read -r line < "/proc/$1/stat" || return 1
    line="${line##*) }"
    set -- $line
    printf '%s' "${20}"
}

cleanup_owned_tmp() {
    local result=$? cleanup_result=0 current_id='' attempt=0
    trap - EXIT INT TERM
    unset MINTED
    # Reaping the body alone is insufficient when a descendant remains.
    # The retained group must disappear before removing its scratch.
    if [[ -n "$OWNED_CHILD_GROUP" ]]; then
        for attempt in {1..40}; do
            kill -0 -- "-$OWNED_CHILD_GROUP" 2>/dev/null || break
            sleep 0.05
        done
        if kill -0 -- "-$OWNED_CHILD_GROUP" 2>/dev/null; then
            echo "::error::owned child group remains; temporary cleanup refused" >&2
            cleanup_result=1
        fi
    fi
    if [ -n "$OWNED_TMPDIR" ]; then
        current_id="$(stat -c '%d:%i:%u:%a' -- "$OWNED_TMPDIR" 2>/dev/null)" || cleanup_result=1
        if [ "$cleanup_result" -eq 0 ] && [ ! -L "$OWNED_TMPDIR" ] && [ -d "$OWNED_TMPDIR" ] &&
           [ -n "$OWNED_TMP_ID" ] && [ "$current_id" = "$OWNED_TMP_ID" ]; then
            /usr/bin/timeout --signal=TERM --kill-after=2s 10s \
                /usr/bin/rm -rf --one-file-system -- "$OWNED_TMPDIR" || cleanup_result=$?
        else
            cleanup_result=1
        fi
        if [ "$cleanup_result" -ne 0 ]; then
            echo "::error::owned temporary cleanup refused or failed" >&2
            [ "$result" -ne 0 ] || result=1
        fi
    fi
    exit "$result"
}

terminate_owned_child() {
    local signal="$1" status="$2" watchdog=""
    trap '' INT TERM
    if [[ -n "$OWNED_CHILD_PID" && "$OWNED_CHILD_BIRTH" =~ ^[0-9]+$ ]] \
        && [[ "$(owned_birth "$OWNED_CHILD_PID" 2>/dev/null || true)" == "$OWNED_CHILD_BIRTH" ]]; then
        kill -s "$signal" -- "-$OWNED_CHILD_PID" 2>/dev/null || true
        # The watchdog checks this exact child's kernel birth before signalling
        # its group, then is reaped by the owning shell on either outcome.
        (
            sleep 2
            if [[ "$OWNED_CHILD_BIRTH" =~ ^[0-9]+$ ]] && [[ "$(owned_birth "$OWNED_CHILD_PID" 2>/dev/null || true)" == "$OWNED_CHILD_BIRTH" ]]; then
                kill -KILL -- "-$OWNED_CHILD_PID" 2>/dev/null || true
            fi
        ) &
        watchdog=$!
        wait "$OWNED_CHILD_PID" 2>/dev/null || true
        kill -TERM -- "-$watchdog" 2>/dev/null || true
        wait "$watchdog" 2>/dev/null || true
    fi
    exit "$status"
}

trap cleanup_owned_tmp EXIT
trap 'terminate_owned_child INT 130' INT
trap 'terminate_owned_child TERM 143' TERM

run_owned_body() {
    local status=0
    # Bash job control creates a group for exactly this owned body, so a
    # termination targets its descendants rather than the runner's group.
    set -m
    (
        set +m
        trap 'unset MINTED' EXIT
        # Keep this exact group leader alive through the watchdog window.
        # Foreground descendants retain their ordinary signal dispositions.
        trap 'unset MINTED; sleep 3' INT TERM
        driver_body
    ) &
    OWNED_CHILD_PID=$!
    OWNED_CHILD_GROUP="$OWNED_CHILD_PID"
    OWNED_CHILD_BIRTH="$(owned_birth "$OWNED_CHILD_PID" 2>/dev/null || true)"
    wait "$OWNED_CHILD_PID" || status=$?
    OWNED_CHILD_PID=""
    return "$status"
}
# END owned temporary-root lifecycle

OWNED_TMPDIR="$(/usr/bin/mktemp -d "${SCRATCH_PREFIX}XXXXXX")"
readonly OWNED_TMPDIR
suffix="${OWNED_TMPDIR#"$SCRATCH_PREFIX"}"
[[ "$OWNED_TMPDIR" = "$SCRATCH_PREFIX"* && "$suffix" =~ ^[[:alnum:]]{6}$ ]]
[ "${OWNED_TMPDIR%/*}" = /tmp ] && [ ! -L "$OWNED_TMPDIR" ] && [ -d "$OWNED_TMPDIR" ]
OWNED_TMP_ID="$(stat -c '%d:%i:%u:%a' -- "$OWNED_TMPDIR")"
[ "${OWNED_TMP_ID##*:}" = 700 ]
[ "$(stat -c '%u' -- "$OWNED_TMPDIR")" = "$(id -u)" ]
readonly OWNED_TMP_ID
export TMPDIR="$OWNED_TMPDIR"

driver_body() {
# No credential exchange is attempted before this full immutable-artifact gate.
"$PY" -I -S -B .github/ci/release-identity.py verify-proof --tag "$RELEASE_TAG" --commit "$RELEASE_COMMIT" --revalidate
DIST=(dist/*.whl dist/*.tar.gz)
[ "${#DIST[@]}" -eq 2 ]
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
}

run_owned_body
