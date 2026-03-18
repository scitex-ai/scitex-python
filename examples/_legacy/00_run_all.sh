#!/usr/bin/env bash
# -*- coding: utf-8 -*-
# Timestamp: 2026-01-24
# File: examples/00_run_all.sh
# Description: Run all example scripts across subdirectories

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

usage() {
    cat <<EOF
Usage: $(basename "$0") [OPTIONS] [DIRECTORY...]

Run example scripts from SciTeX examples directory.

Options:
    -h, --help      Show this help message
    -l, --list      List available example directories
    -d, --dry-run   Show what would be run without executing

Arguments:
    DIRECTORY       Specific directories to run (default: all)

Examples:
    $(basename "$0")                    # Run all examples
    $(basename "$0") bridge session     # Run specific directories
    $(basename "$0") -l                 # List available directories
    $(basename "$0") -d                 # Dry run

EOF
}

list_directories() {
    echo "Available example directories:"
    for dir in */; do
        if [[ -d "$dir" && ! "$dir" =~ ^\. ]]; then
            count=$(find "$dir" -maxdepth 1 -name "*.py" -o -name "*.sh" 2>/dev/null | wc -l)
            printf "  %-20s (%d scripts)\n" "${dir%/}" "$count"
        fi
    done
}

run_directory() {
    local dir="$1"
    local dry_run="${2:-false}"

    if [[ ! -d "$dir" ]]; then
        echo -e "${YELLOW}Skipping: $dir (not found)${NC}"
        return
    fi

    echo -e "\n${GREEN}=== Running examples in: $dir ===${NC}"

    # Check for run_all.sh first
    if [[ -f "$dir/00_run_all.sh" ]]; then
        if [[ "$dry_run" == "true" ]]; then
            echo "  Would run: $dir/00_run_all.sh"
        else
            bash "$dir/00_run_all.sh" || echo -e "${RED}Failed: $dir/00_run_all.sh${NC}"
        fi
        return
    fi

    if [[ -f "$dir/run_all.sh" ]]; then
        if [[ "$dry_run" == "true" ]]; then
            echo "  Would run: $dir/run_all.sh"
        else
            bash "$dir/run_all.sh" || echo -e "${RED}Failed: $dir/run_all.sh${NC}"
        fi
        return
    fi

    # Run numbered Python scripts
    for script in "$dir"/[0-9]*.py; do
        if [[ -f "$script" ]]; then
            if [[ "$dry_run" == "true" ]]; then
                echo "  Would run: python $script"
            else
                echo "  Running: $script"
                python "$script" || echo -e "${RED}Failed: $script${NC}"
            fi
        fi
    done
}

# Parse arguments
DRY_RUN=false
DIRS=()

while [[ $# -gt 0 ]]; do
    case $1 in
    -h | --help)
        usage
        exit 0
        ;;
    -l | --list)
        list_directories
        exit 0
        ;;
    -d | --dry-run)
        DRY_RUN=true
        shift
        ;;
    -*)
        echo "Unknown option: $1"
        usage
        exit 1
        ;;
    *)
        DIRS+=("$1")
        shift
        ;;
    esac
done

# Default to all directories if none specified
if [[ ${#DIRS[@]} -eq 0 ]]; then
    for dir in */; do
        if [[ -d "$dir" && ! "$dir" =~ ^\. ]]; then
            DIRS+=("${dir%/}")
        fi
    done
fi

echo "SciTeX Examples Runner"
echo "======================"
echo "Directories: ${DIRS[*]}"
[[ "$DRY_RUN" == "true" ]] && echo "(DRY RUN MODE)"

for dir in "${DIRS[@]}"; do
    run_directory "$dir" "$DRY_RUN"
done

echo -e "\n${GREEN}Done!${NC}"
