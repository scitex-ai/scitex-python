#!/bin/bash
# Unified module test script - works both locally and in CI
#
# Usage: ./scripts/test-module.sh <mode> <module> [pytest-args...]
#
# Modes:
#   editable  - Install from local source (pip install -e .)
#   pypi      - Install from PyPI (pip install scitex)
#
# Environment:
#   Local: Creates temp venv with isolated deps
#   CI:    Installs deps directly (already isolated)
#
# Examples:
#   ./scripts/test-module.sh editable io -v
#   ./scripts/test-module.sh pypi stats --tb=short
#   make test-isolated MODULE=io           # editable mode
#   make test-isolated-pypi MODULE=io      # pypi mode

set -e

MODE="${1:?Usage: $0 <editable|pypi> <module> [pytest-args...]}"
MODULE="${2:?Usage: $0 <editable|pypi> <module> [pytest-args...]}"
shift 2
PYTEST_ARGS=("$@")

if [[ "$MODE" != "editable" && "$MODE" != "pypi" ]]; then
    echo "Error: Mode must be 'editable' or 'pypi'"
    echo "Usage: $0 <editable|pypi> <module> [pytest-args...]"
    exit 1
fi

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

# Modules with optional extras in pyproject.toml
MODULES_WITH_EXTRAS=(
    ai audio benchmark bridge browser capture cli cloud config db decorators dev dsp dt fig fts gen
    git io linalg msword nn notebook parallel path pd plt repro resource scholar stats str
    torch types utils web writer
)

# Map module names to extras names (for naming conflicts)
# e.g., "dev" module uses "devtools" extras (since "dev" is for pytest tools)
get_extras_name() {
    local module="$1"
    case "$module" in
    dev) echo "devtools" ;;
    *) echo "$module" ;;
    esac
}

# Check if module has extras
has_extras() {
    local module="$1"
    for m in "${MODULES_WITH_EXTRAS[@]}"; do
        [[ "$m" == "$module" ]] && return 0
    done
    return 1
}

# Get install command for module
get_install_cmd() {
    local mode="$1"
    local module="$2"
    local extras_name
    extras_name=$(get_extras_name "$module")

    if [[ "$mode" == "editable" ]]; then
        if has_extras "$module"; then
            echo "-e .[${extras_name}]"
        else
            echo "-e ."
        fi
    else
        # PyPI mode
        if has_extras "$module"; then
            echo "scitex[${extras_name}]"
        else
            echo "scitex"
        fi
    fi
}

# Verify module exists
if [[ ! -d "$PROJECT_ROOT/tests/scitex/$MODULE" ]]; then
    echo "Error: No tests found for module '$MODULE'"
    echo "Available modules:"
    for d in "$PROJECT_ROOT"/tests/scitex/*/; do
        [[ -d "$d" && "$(basename "$d")" != "__pycache__" ]] && basename "$d"
    done | column
    exit 1
fi

INSTALL_CMD=$(get_install_cmd "$MODE" "$MODULE")

run_tests() {
    echo "Installing: pip install $INSTALL_CMD"
    pip install --upgrade pip -q
    # shellcheck disable=SC2086
    pip install $INSTALL_CMD -q
    pip install pytest pytest-cov pytest-timeout -q

    echo ""
    echo "=== Installed packages ==="
    pip list | grep -E "^(scitex|pytest|numpy|pandas|scipy)" || true
    echo ""

    echo "=== Running tests for $MODULE ==="
    cd "$PROJECT_ROOT"
    PYTHONPATH=./src pytest "tests/scitex/$MODULE/" -v --tb=short "${PYTEST_ARGS[@]}" 2>&1 | tee test-results.log
    tail -5 test-results.log
}

# Detect environment
if [[ -n "${GITHUB_ACTIONS:-}" ]]; then
    echo "=== CI Mode ($MODE): Testing module '$MODULE' ==="
    run_tests
else
    echo "=== Local Mode ($MODE): Testing module '$MODULE' in isolation ==="

    VENV_DIR=$(mktemp -d)
    trap 'rm -rf "$VENV_DIR"' EXIT

    echo "Creating temporary environment: $VENV_DIR"
    python3 -m venv "$VENV_DIR"
    # shellcheck source=/dev/null
    source "$VENV_DIR/bin/activate"

    run_tests
fi

echo ""
echo "=== Test completed ==="
