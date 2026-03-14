#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

RED='\033[0;31m'
GREEN='\033[0;32m'
NC='\033[0m'

usage() {
    echo "Usage: $(basename "$0") [-h]"
    echo "Run all demo_figures examples"
    echo ""
    echo "Options:"
    echo "  -h, --help    Show this help"
}

[[ "${1:-}" == "-h" || "${1:-}" == "--help" ]] && {
    usage
    exit 0
}

echo "Running demo_figures examples..."
FAILED=0
for script in [0-9]*.py; do
    [[ -f "$script" ]] || continue
    echo -e "  ${GREEN}Running: $script${NC}"
    python "$script" || {
        echo -e "  ${RED}Failed: $script${NC}"
        FAILED=$((FAILED + 1))
    }
done

[[ $FAILED -eq 0 ]] && echo -e "${GREEN}All examples passed!${NC}" || echo -e "${RED}$FAILED example(s) failed${NC}"
exit $FAILED
