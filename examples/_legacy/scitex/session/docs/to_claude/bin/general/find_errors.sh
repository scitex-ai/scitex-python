#!/bin/bash
# -*- coding: utf-8 -*-
# Timestamp: "2025-06-05 15:31:18 (ywatanabe)"
# File: ./gPAC/find_errors.sh

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

NC='\033[0m'



find_error() {
    ## Error
    error_dirs=$(find . -type d -name "FINISHED_ERROR")
    echo_error "Failed jobs:"
    # echo "$error_dirs" | sed 's|_out/FINISHED_ERROR|.py|g'
    for error_dir in $error_dirs; do
        script_name=$(echo $error_dir | sed 's|_out/FINISHED_ERROR|.py|g')
        echo_error "Error in: $script_name"

        last_run_path=$(find "$error_dir" -maxdepth 1 -name "2025Y-*" -type d | sort | tail -n1)

        if [ -n "$last_run_path" ]; then
            log_dir="$last_run_path/logs"
            stdout="$log_dir/stdout.log"
            stderr="$log_dir/stderr.log"

            # if [ -f "$stdout" ]; then
            #     echo_success "stdout:"
            #     echo_success "$(cat $stdout)"
            # fi

            if [ -f "$stderr" ]; then
                echo_error "stderr:"
                echo_error "$(cat $stderr)"
            fi
        fi
        echo
    done
}


find_running() {
    running_dirs=$(find . -type d -name "RUNNING")
    echo_warning "Running jobs:"
    echo "$running_dirs" | sed 's|_out/RUNNING|.py|g'
}


find_success() {
    success_dirs=$(find . -type d -name "FINISHED_SUCCESS")
    echo_success "Successful jobs:"
    echo "$success_dirs" | sed 's|_out/FINISHED_SUCCESS|.py|g'
}

find_error
find_running
find_success

# EOF
