#!/bin/bash
# -*- coding: utf-8 -*-
# Timestamp: "2025-05-21 00:42:09 (ywatanabe)"
# File: ./.claude/to_claude/bin/safe_rm.sh

THIS_DIR="$(cd $(dirname ${BASH_SOURCE[0]}) && pwd)"
LOG_PATH="$THIS_DIR/.$(basename $0).log"
echo > "$LOG_PATH"

BLACK='\033[0;30m'
LIGHT_GRAY='\033[0;37m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo_info() { echo -e "${LIGHT_GRAY}$1${NC}"; }
echo_success() { echo -e "${GREEN}$1${NC}"; }
echo_warning() { echo -e "${YELLOW}$1${NC}"; }
echo_error() { echo -e "${RED}$1${NC}"; }
# ---------------------------------------

usage() {
    echo_info "Usage: $(basename $0) [-h|--help] file_or_directory [file_or_directory...]"
    echo_info "Options:"
    echo_info "  -h, --help    Display this help message"
    echo_info ""
    echo_info "Example:"
    echo_info "  $(basename $0) file1.txt dir1"
    echo_info "  $(basename $0) *.txt"
    exit 1
}

safe_rm() {
    # Creates timestamped backup of specified files/directories
    # Example: safe_rm file1.txt dir1
    local paths=("$@")
    local timestamp=$(date +"%Y%m%d_%H%M%S")
    for path in "${paths[@]}"; do
        if [ -e "$path" ]; then
            local dir=$(dirname "$path")
            local tgt_dir="$dir/.old"
            local filename=$(basename "$path")
            local ext="${filename##*.}"
            local name="${filename%.*}"

            # Handle files without extension
            if [ "$ext" = "$filename" ]; then
                ext=""
                name="$filename"
            fi

            mkdir -p "$tgt_dir" > /dev/null 2>&1

            if [ -z "$ext" ]; then
                mv -f "$path" "${tgt_dir}/${name}-${timestamp}"
                echo_success "Moved $path to ${tgt_dir}/${name}-${timestamp}"
            else
                mv -f "$path" "${tgt_dir}/${name}-${timestamp}.${ext}"
                echo_success "Moved $path to ${tgt_dir}/${name}-${timestamp}.${ext}"
            fi
        else
            echo_error "Error: $path does not exist"
        fi
    done
}

# Parse arguments
if [ $# -eq 0 ] || [ "$1" = "-h" ] || [ "$1" = "--help" ]; then
    usage
fi

safe_rm "$@" 2>&1 | tee -a "$LOG_PATH"

# EOF
