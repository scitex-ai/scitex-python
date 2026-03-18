#!/bin/bash
# -*- coding: utf-8 -*-
# Timestamp: "2025-05-18 19:41:28 (ywatanabe)"
# File: ./.claude/to_claude/bin/run_tests_python.sh

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

echo_info() { echo -e "${BLACK}$1${NC}"; }

touch "$LOG_PATH" >/dev/null 2>&1


# PATH Configurations
LOG_PATH_TMP="$THIS_DIR/.$(basename $0).log-tmp"
PYTEST_INI_PATH="$THIS_DIR/tests/pytest.ini"

# Default Values
DELETE_CACHE=false
SYNC_TESTS_WITH_SOURCE=false
DEBUG=false
SPECIFIC_TEST=""
ROOT_DIR=$THIS_DIR
N_WORKERS=$(($(nproc) * 25 / 100))  # Use 25% of cores
LAST_FAILED=false
IPDB=false
N_WORKERS=1
N_RUNS=1
EXIT_FIRST=false
ENSURE_EXECUTABLE=false


usage() {
    echo "Usage: $0 [options] [test_path]"
    echo
    echo "Options:"
    echo "  -c, --cache        Delete Python cache files (default: $DELETE_CACHE)"
    echo "  -d, --debug        Run tests in debug mode (default: $DEBUG)"
    echo "  -i, --ipdb         Enable IPython debugger on test failures (default: $IPDB)"
    echo "  -j, --n_workers    Number of workers (default: $N_WORKERS, auto-parallel if >1)"
    echo "  -l, --last_failed  Run only tests that failed in the last run (default: $LAST_FAILED)"
    echo "  -n, --n_runs       Number of test executions (default: $N_RUNS)"
    echo "  -e, --exitfirst    (default: $EXIT_FIRST)"
    echo "  -s, --sync         Sync tests directory with source (default: $SYNC_TESTS_WITH_SOURCE)"
    echo "  -x, --ensure_executable "
    echo "  -h, --help         Display this help message"
    echo
    echo "Arguments:"
    echo "  test_path          Optional path to specific test file or directory"
    echo
    echo "Example:"
    echo "  $0 -c              Clean cache before running tests"
    echo "  $0 -n 10           Run tests 10 times in sequence"
    echo "  $0 -j 4            Run tests in parallel with 4 workers"
    echo "  $0 tests/scitex/core Run only tests in core module"
    exit 1
}

parse_args() {
    while [[ $# -gt 0 ]]; do
        case $1 in
            -c|--cache)
                DELETE_CACHE=true
                shift
                ;;
            -e|--exit_firat)
                EXIT_FIRST=true
                shift
                ;;
            -s|--sync)
                SYNC_TESTS_WITH_SOURCE=true
                shift
                ;;
            -n|--n_workers)
                N_RUNS="$2"
                shift 2
                ;;
            -j|--n_workers)
                N_WORKERS="$2"
                shift 2
                ;;
            -i|--ipdb)
                IPDB=true
                shift
                ;;
            -l|--last_failed)
                LAST_FAILED=true
                shift
                ;;
            -d|--debug)
                DEBUG=true
                shift
                ;;
            -x|--ensure_executable)
                ENSURE_EXECUTABLE==true
                shift
                ;;
            -h|--help)
                usage
                ;;
            *)
                if [[ -e "$1" ]]; then
                    SPECIFIC_TEST="$1"
                    shift
                else
                    echo "Unknown option or file not found: $1"
                    usage
                fi
                ;;
        esac
    done
}


ensure_executable() {
    # Make all Python files executable
    echo_info "Making Python files executable..."
    find "$THIS_DIR/src" "$THIS_DIR/tests" -name "*.py" -type f -exec chmod +x {} \; 2>/dev/null || true
}

ensure_no_existing_runtests_processes() {
    # Get only processes that contain run_tests.sh in the command, excluding grep itself and the current process
    existing_processes=$(ps aux | grep "run_tests.sh" | grep -v "grep" | grep -v $$ | awk '{print $2}')

    if [ -n "$existing_processes" ]; then
        echo_info "Found existing run_tests.sh processes:"
        for pid in $existing_processes; do
            # Double check if process actually exists
            if ps -p $pid > /dev/null; then
                echo_info "PID: $pid"
                return 1
            fi
        done
    fi

    # No legitimate processes found
    return 0
}

kill_existing_runtests_processes() {
    existing_pids=$(ps aux | grep "run_tests.sh" | grep -v "grep" | grep -v $$ | awk '{print $2}')
    if [ -n "$existing_pids" ]; then
        echo_info "Killing existing run_tests.sh processes: $existing_pids"
        kill -9 $existing_pids 2>/dev/null
    fi
}

clear_cache() {
    echo_info "Cleaning Python cache..."
    find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
    find . -name "*.pyc*" -type f -exec rm -f {} + 2>/dev/null || true
}

remove_python_output_directories() {
    echo_info "Delete Python output directories..."
    find "./tests/" -name "test_*_out" -type d -exec rm -rf {} + 2>/dev/null || true
}

sync_tests_with_source() {
    echo_info "Updating test structure..."
    "$THIS_DIR/tests/sync_tests_with_source.sh"
}

run_tests() {
    PYTEST_ARGS="-c $PYTEST_INI_PATH"

    echo_info "pytest.ini:\n$(cat "$PYTEST_INI_PATH")"\
        | tee -a "$LOG_PATH_TMP"

    # Timestamp
    date >> "$LOG_PATH_TMP" 2>&1

    # ROOT DIR
    if [[ -n $ROOT_DIR ]]; then
        echo_info "ROOT_DIR: $ROOT_DIR"
        PYTEST_ARGS+=" --rootdir=$ROOT_DIR"
    fi

    # EXIT_FIRST
    if [[ $EXIT_FIRST == true ]]; then
        PYTEST_ARGS+=" --exitfirst"
    fi

    # N_WORKERS
    if [[ $N_WORKERS -gt 1 ]]; then
        echo_info "Running in parallel mode with $N_WORKERS workers"
        PYTEST_ARGS+=" -n $N_WORKERS"
    fi

    # VERBOSE
    if [[ $DEBUG == true ]]; then
        echo_info "Running in debug verbose mode"
        PYTEST_ARGS+=" --verbose"
    fi

    # LAST_FAILED
    if [[ $LAST_FAILED == true ]]; then
        echo_info "Running in last-failed mode"
        PYTEST_ARGS+=" --last-failed"
    fi

    # IPDB
    if [[ $IPDB == true ]]; then
        echo_info "Running in IPDB mode"
        PYTEST_ARGS+=" --pdb \
                       --pdbcls=IPython.terminal.debugger:TerminalPdb"
    fi

    # SPECIFIC TEST
    if [[ -n "$SPECIFIC_TEST" ]]; then
        echo_info "Running specific test: $SPECIFIC_TEST"
        PYTEST_ARGS+=" $SPECIFIC_TEST"
    fi

    # Main
    echo_warning "Running $PYTEST_ARGS..."
    pytest $PYTEST_ARGS | tee -a "$LOG_PATH_TMP" 2>&1
}

main() {
    echo_info "No existing processes found. Continuing execution."
    parse_args "$@"

    # Kill Existing run_tests.sh
    kill_existing_runtests_processes

    # Kill Existing run_tests.sh
    if ensure_no_existing_runtests_processes; then

        # Delete outputs of test scripts
        remove_python_output_directories

        for i_run in `seq 1 $N_RUNS`; do

            # Clear the temporary log file
            > "$LOG_PATH_TMP"

            # Handle Original Arguments
            echo_info "LOG_PATH: $LOG_PATH" | tee -a "$LOG_PATH_TMP"
            echo_info "LOG_PATH_TMP: $LOG_PATH_TMP" | tee -a "$LOG_PATH_TMP"
            echo_info "Test run $i_run of $N_RUNS" | tee -a "$LOG_PATH_TMP"

            # Ensure all .py scripts are executable
            if [[ $ENSURE_EXECUTABLE == true ]]; then
                ensure_executable
            fi

            # Clear cache
            if [[ $DELETE_CACHE == true ]]; then
                clear_cache
            fi

            # Synchronize test code with source
            if [[ $SYNC_TESTS_WITH_SOURCE == true ]]; then
                sync_tests_with_source
            fi

            # Main
            run_tests

            # Update the latest log symlink
            cat "$LOG_PATH_TMP" > "$LOG_PATH"
            sleep 1

        done

    else
        echo "Exiting to avoid multiple instances."
        exit 1
    fi

}

# Execute main function with all arguments
main "$@"

# EOF
