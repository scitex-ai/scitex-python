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

# Echo the resolved plan: when a run fails on an unfamiliar node, the FIRST
# question is which of the two profiles it took.
echo "exec-in-sif: apptainer=$APPTAINER (via $APPTAINER_FROM)"
echo "exec-in-sif: sif=$SIF"
echo "exec-in-sif: $GPFS_PROJECT $GPFS_STATE"
echo "exec-in-sif: APPTAINER_TMPDIR=$APPTAINER_TMPDIR"
echo "exec-in-sif: + $APPTAINER ${APPTAINER_ARGV[*]} $SIF bash .github/ci/$INNER $*"

exec "$APPTAINER" "${APPTAINER_ARGV[@]}" "$SIF" bash ".github/ci/$INNER" "$@"
