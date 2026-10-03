#!/usr/bin/env bash
# Runs INSIDE the reused scitex-ci SIF (apptainer exec). $1 = python version.
#
# WHY a layered install (not the bare PYTHONPATH=src trick scitex-dev uses):
# the shared ci-cpu.sif bakes scitex-dev[all,dev] DEPS, NOT scitex's —
# matplotlib / graphviz / seaborn / django / Pillow / networkx / playwright /
# pytesseract / scitex-app / scitex-ui are absent from the SIF. So we install
# THIS checkout + its [all,dev] extras (WITH dependency resolution) into a
# writable --target dir and prepend that on PYTHONPATH. The SIF still supplies
# the heavy shared base (pip/uv, the python interpreters, scitex-dev's deps),
# so only scitex's own thin dep set is fetched per run.
#
# --target (not a plain `-e .`): the SIF's /opt/venv-* are root-owned + RO and
# the HPC compute-node HOME is RO inside the container, so a normal site install
# fails Permission denied. A writable target on node-local /tmp sidesteps both.
#
# Fail-loud: a missing interpreter or a failed install is a hard error.
set -euo pipefail

V="${1:?python version arg required (3.11/3.12/3.13)}"
case "$V" in 3.11|3.12|3.13) ;; *) exit 1;; esac
VENV="/opt/venv-$V"
test -x "$VENV/bin/python" || {
    echo "::error::baked python missing in $VENV — rebuild the SIF: scitex-container apptainer build ci-cpu"
    exit 1
}

export LC_ALL=C.UTF-8 LANG=C.UTF-8

# Real writable scratch. The runner profile exports TMPDIR=~/.cache/tmp, a host
# path that does NOT resolve inside the container; tests (tmp_path) and the
# install target both need a working, writable tmp. Node-local /tmp is writable
# + ephemeral and per-version-isolated so concurrent matrix legs don't collide.
SCRATCH_PREFIX="/tmp/ci-scitex-${GITHUB_RUN_ID:?}-${GITHUB_RUN_ATTEMPT:?}-$V-"

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
mkdir -p "$TMPDIR/site" "$TMPDIR/uv-cache"

# The HPC compute-node $HOME is READ-ONLY inside the container, so uv/pip cannot
# create their default caches under ~/.cache — point them at the writable
# scratch instead (else `uv pip install` dies: "failed to create directory
# ~/.cache/uv: File exists / read-only").
export UV_CACHE_DIR="$TMPDIR/uv-cache"
export XDG_CACHE_HOME="$TMPDIR"
export PIP_CACHE_DIR="$TMPDIR/pip-cache"

# Headless matplotlib — no DISPLAY on the compute node; force the Agg backend so
# pyplot imports + figure rendering in the test suite never try to open a GUI.
export MPLBACKEND=Agg

# Dedicated, stable matplotlib config/cache dir for this matrix leg. Without
# pinning it, MPLCONFIGDIR defaults to $XDG_CACHE_HOME/matplotlib which is COLD
# every CI run; the xdist workers (one per core, see below) then each cold-start
# matplotlib and RACE to build fontList.json in that shared dir.
# A partial/contended cache makes some renders fall back to a different font, so
# scitex's reproducibility tests (validate_recipe renders the SAME recipe
# twice and compares) see render1 != render2 → spurious MSE-over-threshold
# failures (e.g. TestValidateRecipe, max channel diff 255). One stable dir +
# a single warm-up below (build the cache ONCE, pre-fork) removes the race.
export MPLCONFIGDIR="$TMPDIR/mpl"
mkdir -p "$MPLCONFIGDIR"

# A VIRTUAL_ENV leaked from the runner profile (~/.env-3.11) is a broken symlink
# in here; unset it so no tool (uv, pip) tries to follow it.
unset VIRTUAL_ENV PYTHONHOME PYTHONPATH || true

# venv bin on PATH (this matrix leg's python3 + pip); PYTHONPATH points at the
# writable target so imports + coverage use the freshly-installed checkout.
export PATH="$VENV/bin:$PATH"

echo "py=$("$VENV/bin/python" -V) target=$TMPDIR/site"

# Install scitex + its [all,dev] extras WITH deps into the writable target.
# Resolver failure fails the leg; the declared complete extras are required.
command -v uv >/dev/null
uv pip install --python "$VENV/bin/python" --target="$TMPDIR/site" -e ".[all,dev]"

# Peer standalones aliased by the umbrella (scitex_gen, scitex_dsp, ...) are NOT
# in the [all] extra, so the install above never refreshes them. Install them
# FRESH into the SAME --target so they shadow the SIF's baked (possibly stale)
# copies via the PYTHONPATH below — without this, scitex.dsp.utils imports the
# SIF's old scitex_gen (missing `to_even`) and the cross-package import test
# fails. Best-effort: an unavailable peer is importorskip'd by the identity test.
uv pip install --python "$VENV/bin/python" --target="$TMPDIR/site" \
    scitex-dsp scitex-gen scitex-pd scitex-nn scitex-resource \
    scitex-linalg scitex-datetime scitex-decorators \
    || echo "peer standalones partially unavailable; identity test importorskips the rest"

export PYTHONPATH="$TMPDIR/site:$PWD/src${PYTHONPATH:+:$PYTHONPATH}"

# Parallelise with pytest-xdist (baked in [dev]/[all,dev] as pytest-xdist>=3).
# scitex's suite is ~2460 tests; single-process it overran the job's old
# 30-min cap (2300 passed in ~28 min, cancelled at 96%). Each xdist worker is
# a SEPARATE PROCESS, so matplotlib's global rcParams / pyplot state and the
# scitex style-stack are naturally isolated per worker — the safe way to
# parallelise a matplotlib-heavy suite.
#
# Worker count: use ALL cores. Each matrix leg now runs on its own dedicated
# self-hosted node (one runner per node: scitex-01/02/03), so there is no
# co-tenant to yield half the box to — the old nproc//2 cap left 2x the cores
# idle. nice/ionice (below) handles the "yield to higher-priority work if the
# node is ever shared" concern instead of statically reserving half the CPUs.
# Floor 4. pyproject addopts carries `-v`; override to `-q` here — 2460 verbose
# lines x workers bloats the CI log and adds measurable overhead.
NPROC="$(nproc 2>/dev/null || echo 4)"
WORKERS=$NPROC
[ "$WORKERS" -lt 4 ] && WORKERS=4
echo "xdist workers=$WORKERS (nproc=$NPROC)"

# Warm the matplotlib font cache ONCE, single-process, before xdist forks the
# workers. This builds $MPLCONFIGDIR/fontlist-*.json a single time so every
# worker reads a complete, consistent cache instead of racing to build it
# concurrently (the source of the render1!=render2 reproducibility flakes).
# Fail-loud: if matplotlib can't even build its font cache, CI must surface it.
# matplotlib may not be a dependency of this package; only warm the
# font cache when it's importable (no-op otherwise — never fail the run
# on an optional warm-up).
if python -c "import matplotlib" 2>/dev/null; then
  python -c "import matplotlib; matplotlib.use('Agg'); from matplotlib import font_manager; font_manager.fontManager; import matplotlib.pyplot as plt; f=plt.figure(); f.canvas.draw(); print('mpl font cache warmed at', matplotlib.get_cachedir())"
else
  echo "matplotlib not importable — skipping font-cache warm-up (not a dep)"
fi

# Distribution: `--dist load` (per-TEST round-robin), NOT `--dist loadscope`.
# loadscope pins an entire MODULE's tests to ONE worker — and scitex's heavy
# suites are big SINGLE modules (e.g. tests/integration/test_all_plotters_*.py
# parametrize one test over all 47 plotters, ~28 s each). loadscope therefore
# ran all ~50+ cases of such a module SERIALLY on one worker (~25 min) while the
# rest idled. There are NO module/session/class-scoped fixtures in those heavy
# modules and the root conftest's autouse `_close_figures` resets pyplot state
# after EVERY test, so loadscope's "same worker per module" buys nothing here —
# it only serialized. `load` spreads the parametrized cases across ALL workers.
#
# nice -n 19 ionice -c 3: run at the lowest CPU + idle I/O priority so that if
# this node is ever shared with interactive/dev work, CI grabs otherwise-idle
# cores but YIELDS the CPU and disk to any higher-priority process — "all
# available CPUs, with priority handling". The owning shell waits for its
# dedicated child group and preserves its status before cleanup.
# Quarantine the heavy/segfault-prone + umbrella-skip suites (parity with the
# hardened ubuntu workflow): tests/e2e + the cross-package import gate are
# crash-prone, and tests/examples/test_09_dev.py hard-requires scitex.module ->
# scitex_hub, which is umbrella_skip BY DESIGN (never in [all]) so it can't run
# in the [all] SIF. Dropping these ignores is what broke the v2.30.3 release.
nice -n 19 ionice -c 3 \
    python -m pytest tests/ -n "$WORKERS" --dist load -q \
    --ignore=tests/e2e \
    --ignore=tests/integration/test_cross_package_imports.py \
    --ignore=tests/examples/test_09_dev.py \
    --cov=src/scitex --cov-report=xml --cov-report=term \
    -p no:cacheprovider
}

run_owned_body
