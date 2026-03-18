#!/bin/bash
# -*- coding: utf-8 -*-
# Timestamp: "2025-07-14 15:00:41 (ywatanabe)"
# File: ./examples/sync_examples_with_source.sh

ORIG_DIR="$(pwd)"
THIS_DIR="$(cd $(dirname ${BASH_SOURCE[0]}) && pwd)"
LOG_PATH="$THIS_DIR/.$(basename $0).log"
echo > "$LOG_PATH"

GIT_ROOT="$(git rev-parse --show-toplevel 2>/dev/null)"

# Color scheme
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

THIS_DIR="./examples"
ROOT_DIR="$(realpath $THIS_DIR/..)"
cmd="cd $ROOT_DIR" && echo "$cmd" && eval "$cmd"

########################################
# Usage & Argument Parser
########################################
# Default Values
DO_MOVE=false
SRC_DIR="$(realpath "${THIS_DIR}/../src/scitex")"
EXAMPLES_DIR="$(realpath "${THIS_DIR}/../examples/scitex")"
# Use half of available CPU cores by default (minimum 1)
CPU_COUNT=$(nproc 2>/dev/null || sysctl -n hw.ncpu 2>/dev/null || echo 4)
PARALLEL_JOBS=$(( CPU_COUNT / 2 > 0 ? CPU_COUNT / 2 : 1 ))

usage() {
    echo "Usage: $0 [options]"
    echo
    echo "Creates example file structure mirroring source files for module-specific examples."
    echo
    echo "Options:"
    echo "  -m, --move         Move stale example files to .old directory instead of just reporting (default: $DO_MOVE)"
    echo "  -s, --source DIR   Specify custom source directory (default: $SRC_DIR)"
    echo "  -e, --examples DIR Specify custom examples directory (default: $EXAMPLES_DIR)"
    echo "  -j, --jobs N       Number of parallel jobs (default: $PARALLEL_JOBS)"
    echo "  -h, --help         Display this help message"
    echo
    echo "Example:"
    echo "  $0 --move"
    echo "  $0 --source /path/to/src --examples /path/to/examples"
    echo "  $0 -j \$((CPU_COUNT))  # Use all CPU cores"
    exit 1
}

while [[ $# -gt 0 ]]; do
    case $1 in
        -m|--move)
            DO_MOVE=true
            shift
            ;;
        -s|--source)
            SRC_DIR="$2"
            shift 2
            ;;
        -e|--examples)
            EXAMPLES_DIR="$2"
            shift 2
            ;;
        -j|--jobs)
            PARALLEL_JOBS="$2"
            shift 2
            ;;
        -h|--help)
            usage
            ;;
        *)
            echo "Unknown option: $1"
            usage
            ;;
    esac
done

# Set default directories if not specified
if [ -z "$SRC_DIR" ]; then
    cmd="cd $ROOT_DIR" && echo "$cmd" && eval "$cmd"
fi

########################################
# Example Structure
########################################
prepare_examples_structure_as_source() {
    [ ! -d "$SRC_DIR" ] && echo "Source directory not found: $SRC_DIR" && exit 1
    construct_blacklist_patterns
    find "$SRC_DIR" -type d "${FIND_EXCLUDES[@]}" | while read -r dir; do
        examples_dir="${dir/$SRC_DIR/$EXAMPLES_DIR}"
        mkdir -p "$examples_dir"
    done
}

########################################
# Example Template
########################################

update_example_file() {
    local example_file=$1
    local src_file=$2

    if [ ! -f "$example_file" ]; then
        # If file doesn't exist, create it with template
        echo "$example_file not found. Creating..."
        mkdir -p "$(dirname "$example_file")"

        # Create with example template
        touch "$example_file"
        chmod +x "$example_file"
        echo_success "Created: $example_file"
    else
        echo_info "Exists: $example_file (preserving existing content)"
    fi
}

########################################
# Finder
########################################
construct_blacklist_patterns() {
    local EXCLUDE_PATHS=(
        "*/.*"
        "*/.*/*"
        "*/deprecated*"
        "*/archive*"
        "*/backup*"
        "*/tmp*"
        "*/temp*"
        "*/RUNNING/*"
        "*/FINISHED/*"
        "*/FINISHED_SUCCESS/*"
        "*/2025Y*"
        "*/2024Y*"
        "*/__pycache__/*"
        "*/__init__.py"  # Skip __init__.py files for examples
    )

    FIND_EXCLUDES=()
    PRUNE_ARGS=()
    for path in "${EXCLUDE_PATHS[@]}"; do
        FIND_EXCLUDES+=( -not -path "$path" )
        PRUNE_ARGS+=( -path "$path" -o )
    done
    unset 'PRUNE_ARGS[${#PRUNE_ARGS[@]}-1]'
}

find_files() {
    local search_path=$1
    local type=$2
    local name_pattern=$3

    construct_blacklist_patterns
    find "$search_path" \
        \( "${PRUNE_ARGS[@]}" \) -prune -o -type "$type" -name "$name_pattern" -print
}

########################################
# Clean-upper
########################################
move_stale_example_files_to_old() {
    local timestamp="$(date +%Y%m%d_%H%M%S)"
    local stale_count=0
    local moved_count=0
    local stale_files=()

    # Collect stale files first
    while IFS= read -r example_path; do
        # Determine corresponding source file
        example_rel_path="${example_path#$EXAMPLES_DIR/}"
        example_rel_dir="$(dirname $example_rel_path)"
        example_filename="$(basename $example_rel_path)"

        # Extract module name from example filename
        src_filename="${example_filename#example}"
        if [[ ! "$src_filename" =~ ^_ ]]; then
            src_filename="_${src_filename}"
        fi

        src_rel_dir="$example_rel_dir"
        src_rel_path="$src_rel_dir/$src_filename"
        src_path="$SRC_DIR/$src_rel_path"

        if [ ! -f "$src_path" ] && [ -f "$example_path" ]; then
            stale_files+=("$example_path")
            ((stale_count++))
        fi
    done < <(find "$EXAMPLES_DIR" -name "example_*.py" -not -path "*.old*" 2>/dev/null)

    # Report stale files
    if [ $stale_count -gt 0 ]; then
        echo ""
        echo_header "Stale Example Files ($stale_count found)"
        echo ""
        for stale_path in "${stale_files[@]}"; do
            local rel_path="${stale_path#$EXAMPLES_DIR/}"
            if [ "$DO_MOVE" = "true" ]; then
                stale_filename="$(basename $stale_path)"
                stale_path_dir="$(dirname $stale_path)"
                old_dir_with_timestamp="$stale_path_dir/.old-$timestamp"
                tgt_path="$old_dir_with_timestamp/$stale_filename"

                mkdir -p "$old_dir_with_timestamp"
                mv "$stale_path" "$tgt_path"
                echo_success "  [MOVED] $rel_path"
                ((moved_count++))
            else
                echo_warning "  [STALE] $rel_path"
            fi
        done
        echo ""
        if [ "$DO_MOVE" = "false" ]; then
            echo_info "To move stale files, run: $0 -m"
        else
            echo_success "Moved $moved_count stale example files"
        fi
        echo ""
    fi
}

########################################
# Parallel Processing Helper
########################################
# Process a single source file (called in parallel)
process_single_example() {
    local src_file="$1"
    local SRC_DIR="$2"
    local EXAMPLES_DIR="$3"

    # Skip __init__.py files
    [[ "$(basename "$src_file")" == "__init__.py" ]] && return

    # Skip if in subdirectory we don't want examples for
    [[ "$src_file" =~ /PackageHandlers/ ]] && return

    # derive relative path and parts
    rel="${src_file#$SRC_DIR/}"
    rel_dir=$(dirname "$rel")
    src_base=$(basename "$rel")

    # ensure example subdir exists
    examples_dir="$EXAMPLES_DIR/$rel_dir"
    mkdir -p "$examples_dir"

    # build correct example file path
    example_base="example_${src_base}"
    example_file="$examples_dir/$example_base"

    # Process the file
    if [ ! -f "$example_file" ]; then
        mkdir -p "$(dirname "$example_file")"
        touch "$example_file"
        chmod +x "$example_file"
        echo "SUCC: Created: $example_file"
    fi
}
export -f process_single_example

########################################
# Main
########################################
main() {
    local do_move=${1:-false}
    local start_time=$(date +%s)

    echo ""
    echo_header "Examples Synchronization"
    echo ""
    echo_info "Source:    $SRC_DIR"
    echo_info "Examples:  $EXAMPLES_DIR"
    echo_info "Jobs:      $PARALLEL_JOBS"
    echo ""
    echo_info "Note: Creates placeholder example files for each source module."
    echo ""

    # Create examples directory if it doesn't exist
    mkdir -p "$EXAMPLES_DIR"

    echo_info "Synchronizing example files (parallel)..."
    local file_count=$(find_files "$SRC_DIR" f "*.py" | wc -l)
    find_files "$SRC_DIR" f "*.py" | \
        xargs -P "$PARALLEL_JOBS" -I {} bash -c 'process_single_example "$@"' _ {} "$SRC_DIR" "$EXAMPLES_DIR"
    echo_success "Processed $file_count source files"

    # Clean up stale files
    move_stale_example_files_to_old

    local end_time=$(date +%s)
    local elapsed=$((end_time - start_time))

    echo_header "Summary"
    echo_success "Completed in ${elapsed}s"
    echo ""

    tree "$THIS_DIR" -I "outputs|__pycache__|*.pyc|.old*" 2>&1 >> "$LOG_PATH"
}

main "$@"
cd $ORIG_DIR

# EOF
