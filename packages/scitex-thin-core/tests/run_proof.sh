#!/usr/bin/env bash
# Clean-venv proof for the thin `scitex` core prototype.
#
#   run_proof.sh <scratch-dir> <scitex-io-src> <scitex-str-src>
#
# Builds three LOCAL wheels (thin core 3.0.0.dev0, scitex-io and scitex-str
# from their prototype branches). Each matrix leg gets a fresh `uv venv` (no
# system/user site-packages) and its OWN --find-links dir holding only the
# wheels that leg is allowed to see, and installs ONLY the leaf wheel(s). The
# thin core is pulled in transitively; the 2.x umbrella on PyPI cannot satisfy
# `scitex>=3.0.0.dev0`, so a pass proves the local core was used. Any other
# transitive SciTeX dependency comes from PyPI as released today (i.e.
# WITHOUT a `scitex.modules` entry point). Nothing is uploaded anywhere.
set -euo pipefail

SCR=${1:?scratch dir}
IO_SRC=${2:?scitex-io source tree}
STR_SRC=${3:?scitex-str source tree}
HERE=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
CORE_SRC=$(dirname "$HERE")
PY=${PY:-/usr/bin/python3.12}
UV=${UV:-uv}
WHEELS="$SCR/wheels"

rm -rf "$SCR" && mkdir -p "$WHEELS"
export PROOF_SCRATCH="$SCR" PYTHONNOUSERSITE=1

echo "== build wheels ($($UV --version); $($PY -I --version))"
for src in "$CORE_SRC" "$IO_SRC" "$STR_SRC"; do
    "$UV" build -q --wheel --python "$PY" -o "$WHEELS" "$src"
done
ls -1 "$WHEELS"

CORE_WHL=$(ls "$WHEELS"/scitex-3.0.0.dev0-*.whl)
IO_WHL=$(ls "$WHEELS"/scitex_io-*.whl)
STR_WHL=$(ls "$WHEELS"/scitex_str-*.whl)

rc=0
# leg <name> <expected names|-> <visible wheels (comma-sep)> <wheels to install...>
leg() {
    local name=$1 expected=$2 visible=$3
    shift 3
    local venv="$SCR/venv-$name" links="$SCR/links-$name"
    mkdir -p "$links"
    IFS=, read -ra vis <<<"$visible"
    for w in "${vis[@]}"; do cp "$w" "$links/"; done
    echo
    echo "== leg: $name"
    echo "   install: $(for w in "$@"; do basename "$w"; done | tr '\n' ' ')"
    echo "   local wheels visible: $(ls "$links" | tr '\n' ' ')"
    "$UV" venv -q --python "$PY" "$venv"
    "$UV" pip install -q --python "$venv/bin/python" --find-links "$links" "$@"
    "$UV" pip list --python "$venv/bin/python" 2>/dev/null | awk 'tolower($1) ~ /^scitex($|[-_])/' | tr -s ' ' | paste -sd ' ' | sed 's/^/   scitex-* installed: /'
    (cd "$SCR" && "$venv/bin/python" -I "$HERE/check_clean_venv.py" "$expected") || rc=1
}

leg core-only - "$CORE_WHL" "$CORE_WHL"
leg io-only io "$CORE_WHL,$IO_WHL" "$IO_WHL"
leg io-and-str io,str "$CORE_WHL,$IO_WHL,$STR_WHL" "$IO_WHL" "$STR_WHL"

echo
echo "== OVERALL: $([ $rc -eq 0 ] && echo 'ALL LEGS PASS' || echo 'SOME LEG FAILED')"
exit $rc
