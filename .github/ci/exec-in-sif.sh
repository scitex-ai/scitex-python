#!/usr/bin/env bash
# Outer apptainer-exec wrapper for scitex's self-hosted CI.
#
# Runs ON THE RUNNER (outside the SIF). Resolves apptainer + the SIF image, then
# `apptainer exec`s the SIF and hands off to an INNER script (run inside the
# container). Keeps every workflow job's YAML down to one line —
# `bash .github/ci/exec-in-sif.sh <inner-script> [args...]` — and concentrates
# all the SIF plumbing (apptainer resolution, ~-expansion, scratch, binds) in
# one version-controlled place.
#
# HOST-AGNOSTIC. This script is NOT Spartan-only: it auto-adapts to whichever
# self-hosted runner picks the job up, keyed off what actually exists on the box.
#
#   * Spartan HPC — the GPFS project dir /data/gpfs/projects/punim0264 EXISTS:
#     apptainer comes from the ~/.env-3.11 shim named by SCITEX_CI_APPTAINER,
#     apptainer scratch lives on the GPFS project, and punim0264 is bound into
#     the container ($HOME/.scitex there is a symlink into it, so without the
#     bind the symlink dangles inside the SIF).
#
#   * Local compute nodes (scitex-compute-01..04) — NO /data/gpfs at all:
#     apptainer is the distro package on PATH (/usr/bin/apptainer), scratch is
#     host-local under $HOME/.cache/scitex-ci, and the GPFS bind is OMITTED
#     (apptainer refuses a bind whose source does not exist, and `mkdir -p` on a
#     GPFS scratch path would hard-fail here under `set -e`).
#
# Each of those three decisions (interpreter, scratch, bind) is made
# INDEPENDENTLY from a probe of this host, so a runner that matches neither
# profile exactly still gets a coherent command line.
#
# Env (set by the workflow from repo Actions Variables):
#   SCITEX_CI_APPTAINER   OPTIONAL path to an apptainer shim
#                         (e.g. ~/.env-3.11/bin/apptainer). Honoured when it
#                         points at an executable; otherwise apptainer is taken
#                         from PATH.
#   SCITEX_CI_SIF         REQUIRED path to the CI SIF image
#                         (e.g. ~/.scitex/dev/containers/ci-cpu.sif)
#
# Usage:
#   bash .github/ci/exec-in-sif.sh run-in-sif.sh 3.12
#
# Fail-loud (operator directive): if NEITHER the shim nor PATH yields an
# apptainer, or the SIF is missing, that is a HARD error naming what was tried
# — never a silent fallback to a bare-runner install.
set -euo pipefail

INNER="${1:?inner script name required (relative to .github/ci/)}"
shift || true
case "$INNER" in run-in-sif.sh|build-in-sif.sh|publish-in-sif.sh) ;; *) echo "::error::unowned inner script"; exit 1;; esac
case "${1:-}" in 3.11|3.12|3.13) ;; *) echo "::error::unsupported Python version"; exit 1;; esac

# Spartan's job shell is --noprofile --norc (no Lmod), so its apptainer shim dir
# must be put on PATH explicitly; the shim execs the real Apptainer binary.
# Harmless where that directory is absent — a non-existent PATH entry is simply
# never matched — which is the case on the local compute nodes.
export PATH="$HOME/.env-3.11/bin:$PATH"

# ~-expand the Actions-Variable paths: a quoted "~/…" is NOT tilde-expanded by
# the shell, so substitute a leading ~ with $HOME ourselves.
APPTAINER_VAR="${SCITEX_CI_APPTAINER:-}"
APPTAINER_VAR="${APPTAINER_VAR/#\~/$HOME}"
SIF="${SCITEX_CI_SIF:?SCITEX_CI_SIF not set (repo Actions Variable)}"
SIF="${SIF/#\~/$HOME}"

# Apptainer resolution, in order:
#   1. SCITEX_CI_APPTAINER when it names an executable  (Spartan's shim)
#   2. `apptainer` on PATH                              (local compute nodes)
# Only when NEITHER resolves is this an error — and the message names BOTH
# attempts, because "which one did you even try" is the whole diagnosis.
if [ -n "$APPTAINER_VAR" ] && [ -x "$APPTAINER_VAR" ]; then
    APPTAINER="$APPTAINER_VAR"
    APPTAINER_FROM="SCITEX_CI_APPTAINER"
elif APPTAINER="$(command -v apptainer 2>/dev/null)"; then
    APPTAINER_FROM="PATH"
else
    echo "::error::no apptainer on this runner. Tried (1) SCITEX_CI_APPTAINER=${SCITEX_CI_APPTAINER:-<unset>} (expanded to '${APPTAINER_VAR:-<empty>}') — not an executable; (2) 'apptainer' on PATH ($PATH) — not found. Install apptainer on this runner, or point SCITEX_CI_APPTAINER at a working shim. Running the job outside the SIF on a bare-runner install is NOT an acceptable fallback."
    exit 1
fi

[ -f "$SIF" ] || {
    echo "::error::CI SIF missing at $SIF — rebuild it: scitex-container apptainer build ci-cpu"
    exit 1
}

# Release jobs use a reviewed content-addressed image; no mutable alias is
# executed after verification. Other existing SIF callers keep their contract.
if [ -n "${SCITEX_CI_SIF_SHA256:-}" ]; then
    [[ "$SCITEX_CI_SIF_SHA256" =~ ^[0-9a-f]{64}$ ]] || exit 1
    SIF="$(realpath -- "$SIF")"
    [ "$(basename -- "$SIF")" = "ci-cpu-sha256-$SCITEX_CI_SIF_SHA256.sif" ] || {
        echo "::error::release requires the content-addressed CI SIF"; exit 1;
    }
    ACTUAL_SIF_SHA="$(sha256sum -- "$SIF")"
    [ "${ACTUAL_SIF_SHA%% *}" = "$SCITEX_CI_SIF_SHA256" ] || {
        echo "::error::release CI SIF byte identity differs"; exit 1;
    }
fi

# Apptainer scratch. On Spartan the GPFS project scratch (shared FS) keeps HOME
# clean; everywhere else that path does not exist, and `mkdir -p` under it would
# be a hard failure, so fall back to host-local scratch under $HOME.
GPFS_PROJECT="/data/gpfs/projects/punim0264"
if [ -d "$GPFS_PROJECT" ]; then
    export APPTAINER_TMPDIR="$GPFS_PROJECT/ywatanabe/ci/apptainer-tmp"
else
    export APPTAINER_TMPDIR="$HOME/.cache/scitex-ci/apptainer-tmp"
fi
mkdir -p "$APPTAINER_TMPDIR"

# Build the argv as an ARRAY so the GPFS bind can be dropped cleanly rather than
# passed as an empty string. --pwd "$PWD" keeps the checkout as cwd.
APPTAINER_ARGV=(exec --pwd "$PWD")
if [ -d "$GPFS_PROJECT" ]; then
    APPTAINER_ARGV+=(--bind "$GPFS_PROJECT")
    GPFS_STATE="present (scratch on GPFS, punim0264 bound)"
else
    GPFS_STATE="absent (scratch under \$HOME, no GPFS bind)"
fi

# Test-driver scratch and shared uv cache (#430). Release drivers
# (build/publish) are unchanged: host /tmp, per-leg cache.
#
# One host directory, ROOT, is bound into the container as a SINGLE mount:
#   ROOT/uv-cache  ONE persistent uv cache per host, shared by every runner.
#                  uv documents its cache as safe for concurrent readers and
#                  writers.
#   ROOT/tmp       parent of each leg's owned scratch (install target, tmp),
#                  which the driver removes on exit.
# A single mount matters: uv links the install target out of the cache, and
# link(2) fails with EXDEV across mount points even on one filesystem (measured:
# two binds made uv fall back to a full copy). Linked, a warm leg no longer
# re-downloads and unpacks the ~12 GiB [all,dev] closure.
#
# ROOT = CI_SCRATCH_ROOT (runner .env; e.g. /scratch/<user>/ci-scratch to keep CI
#        off the root filesystem), else $HOME/.cache/scitex-ci on the compute
#        nodes. Spartan (GPFS, no CI_SCRATCH_ROOT) keeps host /tmp and the
#        per-leg cache: its GPFS spans nodes and is not node-local.
UV_CACHE_STATE="per-leg (driver default)"
unset SCITEX_CI_SCRATCH_ROOT SCITEX_CI_UV_CACHE_DIR
if [ "$INNER" = run-in-sif.sh ]; then
    CI_ROOT="${CI_SCRATCH_ROOT:-}"
    if [ -z "$CI_ROOT" ] && [ ! -d "$GPFS_PROJECT" ]; then
        CI_ROOT="$HOME/.cache/scitex-ci"
    fi
    if [ -n "$CI_ROOT" ]; then
        [[ "$CI_ROOT" = /* ]] || { echo "::error::CI_SCRATCH_ROOT must be absolute: $CI_ROOT"; exit 1; }
        mkdir -p "$CI_ROOT"
        CI_ROOT="$(realpath -- "$CI_ROOT")"
        mkdir -p -m 700 "$CI_ROOT/tmp" "$CI_ROOT/uv-cache"
        for d in "$CI_ROOT/tmp" "$CI_ROOT/uv-cache"; do
            [ -d "$d" ] && [ ! -L "$d" ] || { echo "::error::$d must be a real directory"; exit 1; }
        done
        # A killed job cannot run its EXIT trap. Sweep owned scratch that no
        # leg can still be using (job timeout 45 min; threshold 1 day).
        find "$CI_ROOT/tmp" -mindepth 1 -maxdepth 1 -type d -name 'ci-scitex-*' -mmin +1440 \
            -exec rm -rf --one-file-system -- {} + 2>/dev/null || true
        APPTAINER_ARGV+=(--bind "$CI_ROOT")
        export SCITEX_CI_SCRATCH_ROOT="$CI_ROOT/tmp"
        export SCITEX_CI_UV_CACHE_DIR="$CI_ROOT/uv-cache"
        UV_CACHE_STATE="shared $SCITEX_CI_UV_CACHE_DIR, scratch $SCITEX_CI_SCRATCH_ROOT (one bind: $CI_ROOT)"
    fi
fi

# Echo the resolved plan: when a run fails on an unfamiliar node, the FIRST
# question is which of the two profiles it took.
echo "exec-in-sif: apptainer=$APPTAINER (via $APPTAINER_FROM)"
echo "exec-in-sif: sif=$SIF"
echo "exec-in-sif: $GPFS_PROJECT $GPFS_STATE"
echo "exec-in-sif: APPTAINER_TMPDIR=$APPTAINER_TMPDIR"
echo "exec-in-sif: uv cache $UV_CACHE_STATE"
echo "exec-in-sif: + $APPTAINER ${APPTAINER_ARGV[*]} $SIF bash .github/ci/$INNER $*"

exec "$APPTAINER" "${APPTAINER_ARGV[@]}" "$SIF" bash ".github/ci/$INNER" "$@"
