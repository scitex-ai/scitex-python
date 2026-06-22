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
export TMPDIR="/tmp/ci-scitex-${GITHUB_RUN_ID:-0}-${GITHUB_RUN_ATTEMPT:-0}-$V"
rm -rf "$TMPDIR"
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
unset VIRTUAL_ENV || true

# venv bin on PATH (this matrix leg's python3 + pip); PYTHONPATH points at the
# writable target so imports + coverage use the freshly-installed checkout.
export PATH="$VENV/bin:$PATH"

echo "py=$("$VENV/bin/python" -V) target=$TMPDIR/site"

# Install scitex + its [all,dev] extras WITH deps into the writable target.
# Fallback chain mirrors scitex's historical bare-uv/pip workflow so a
# packaging hiccup in an optional extra doesn't strand CI: [all,dev] → [dev] →
# bare. uv first (fast resolver), pip as a final safety net.
uv pip install --python "$VENV/bin/python" --target="$TMPDIR/site" -e ".[all,dev]" ||
    uv pip install --python "$VENV/bin/python" --target="$TMPDIR/site" -e ".[dev]" ||
    uv pip install --python "$VENV/bin/python" --target="$TMPDIR/site" -e "." ||
    pip install --target="$TMPDIR/site" -e ".[dev]"

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
# available CPUs, with priority handling". exec replaces the shell with nice,
# which execs ionice, which execs python (still PID-traceable, signals/exit
# code propagate to the runner step).
exec nice -n 19 ionice -c 3 \
    python -m pytest tests/ -n "$WORKERS" --dist load -q \
    --cov=src/scitex --cov-report=xml --cov-report=term \
    -p no:cacheprovider
