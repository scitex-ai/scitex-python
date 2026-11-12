#!/usr/bin/env bash
# Shared normal build-tool provisioning for producer and independent verifier.
# Called only inside each driver's existing exclusive owned TMPDIR lifecycle.
prepare_docs_environment() {
    local source_python="$1"
    : "${TMPDIR:?owned temporary root required}"
    [ -d "$TMPDIR" ] && [ ! -L "$TMPDIR" ]
    [ ! -e "$TMPDIR/docs-env" ] && [ ! -L "$TMPDIR/docs-env" ]
    "$source_python" -I -S -B -c 'import tomllib; x=tomllib.load(open("pyproject.toml","rb")); assert x["build-system"] == {"requires":["hatchling==1.33.0"],"build-backend":"hatchling.build"}'
    export PYTHONDONTWRITEBYTECODE=1
    export PYTHONPYCACHEPREFIX="$TMPDIR/docs-runtime-pycache"
    uv venv --python "$source_python" "$TMPDIR/docs-env"
    DOC_PY="$TMPDIR/docs-env/bin/python"
    uv pip install --python "$DOC_PY" build hatchling==1.33.0
    "$DOC_PY" -I -B -X "pycache_prefix=$PYTHONPYCACHEPREFIX" - "$TMPDIR/docs-requirements.txt" <<'PYDOC'
import sys
from pathlib import Path
from packaging.requirements import Requirement
from hatchling.build import get_requires_for_build_sdist, get_requires_for_build_wheel
requirements = sorted(set(get_requires_for_build_sdist() + get_requires_for_build_wheel()))
for raw in requirements:
    requirement = Requirement(raw)
    if "\n" in raw or "\r" in raw or requirement.url is not None:
        raise ValueError("unreviewed documentation build requirement")
Path(sys.argv[1]).write_text("\n".join(requirements) + "\n")
PYDOC
    uv pip install --python "$DOC_PY" -r "$TMPDIR/docs-requirements.txt"
}
