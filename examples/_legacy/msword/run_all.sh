#!/bin/bash
# -*- coding: utf-8 -*-
# Timestamp: "2025-12-11 08:28:53 (ywatanabe)"
# File: ./examples/msword/run_all.sh

ORIG_DIR="$(pwd)"
THIS_DIR="$(cd $(dirname ${BASH_SOURCE[0]}) && pwd)"
LOG_PATH="$THIS_DIR/.$(basename $0).log"
echo > "$LOG_PATH"

GIT_ROOT="$(git rev-parse --show-toplevel 2>/dev/null)"

GRAY='\033[0;90m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo_info() { echo -e "${GRAY}INFO: $1${NC}"; }
echo_success() { echo -e "${GREEN}SUCC: $1${NC}"; }
echo_warning() { echo -e "${YELLOW}WARN: $1${NC}"; }
echo_error() { echo -e "${RED}ERRO: $1${NC}"; }
echo_header() { echo_info "=== $1 ==="; }
# ---------------------------------------

main() {
    cd "$THIS_DIR"

    echo_header "Running MS Word Examples"

    # Find all numbered Python scripts (01_*.py, 02_*.py, etc.)
    SCRIPTS=$(ls -1 [0-9][0-9]_*.py 2>/dev/null | sort)

    if [ -z "$SCRIPTS" ]; then
        echo_error "No Python scripts found in $THIS_DIR"
        exit 1
    fi

    # Count scripts
    TOTAL=$(echo "$SCRIPTS" | wc -l)
    CURRENT=0
    FAILED=0

    for script in $SCRIPTS; do
        CURRENT=$((CURRENT + 1))
        echo ""
        echo_header "[$CURRENT/$TOTAL] Running: $script"

        if python "$script" 2>&1 | tee -a "$LOG_PATH"; then
            echo_success "Completed: $script"
        else
            echo_error "Failed: $script"
            FAILED=$((FAILED + 1))
        fi
    done

    echo ""
    echo_header "Summary"
    echo_info "Total: $TOTAL, Passed: $((TOTAL - FAILED)), Failed: $FAILED"
    echo_info "Log: $LOG_PATH"

    if [ $FAILED -gt 0 ]; then
        echo_error "Some examples failed. Check log for details."
        exit 1
    else
        echo_success "All examples completed successfully!"
    fi

    cd "$ORIG_DIR"
}

main "$@"

# EOF
