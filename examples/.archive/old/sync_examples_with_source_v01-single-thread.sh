#!/bin/bash
# -*- coding: utf-8 -*-
# Timestamp: "2025-07-14 15:00:41 (ywatanabe)"
# File: ./examples/sync_examples_with_source.sh

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

touch "$LOG_PATH" >/dev/null 2>&1

THIS_DIR="./examples"
ORIG_DIR="$(pwd)"
ROOT_DIR="$(realpath $THIS_DIR/..)"
cmd="cd $ROOT_DIR" && echo "$cmd" && eval "$cmd"

# Set up colors for terminal output
PURPLE='\033[0;35m'

########################################
# Usage & Argument Parser
########################################
# Default Values
DO_MOVE=false
SRC_DIR="$(realpath "${THIS_DIR}/../src/scitex")"
EXAMPLES_DIR="$(realpath "${THIS_DIR}/../examples/scitex")"

usage() {
    echo "Usage: $0 [options]"
    echo
    echo "Creates example file structure mirroring source files for module-specific examples."
    echo
    echo "Options:"
    echo "  -m, --move         Move stale example files to .old directory instead of just reporting (default: $DO_MOVE)"
    echo "  -s, --source DIR   Specify custom source directory (default: $SRC_DIR)"
    echo "  -e, --examples DIR Specify custom examples directory (default: $EXAMPLES_DIR)"
    echo "  -h, --help         Display this help message"
    echo
    echo "Example:"
    echo "  $0 --move"
    echo "  $0 --source /path/to/src --examples /path/to/examples"
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

    find "$EXAMPLES_DIR" -name "example_*.py" -not -path "*.old*" | while read -r example_path; do

        # Determine corresponding source file
        example_rel_path="${example_path#$EXAMPLES_DIR/}"
        example_rel_dir="$(dirname $example_rel_path)"
        example_filename="$(basename $example_rel_path)"

        # Extract module name from example filename
        # Assuming pattern: example_ModuleName.py -> _ModuleName.py
        src_filename="${example_filename#example}"
        if [[ ! "$src_filename" =~ ^_ ]]; then
            src_filename="_${src_filename}"
        fi

        src_rel_dir="$example_rel_dir"
        src_rel_path="$src_rel_dir/$src_filename"
        src_path="$SRC_DIR/$src_rel_path"

        if [ ! -f "$src_path" ] && [ -f "$example_path" ]; then
            stale_example_path=$example_path
            stale_example_filename="$(basename $stale_example_path)"
            stale_example_path_dir="$(dirname $stale_example_path)"
            old_dir_with_timestamp="$stale_example_path_dir/.old-$timestamp"
            tgt_path="$old_dir_with_timestamp/$stale_example_filename"

            echo -e "${RED}Stale Example       : $stale_example_path${NC}"
            echo -e "${RED}If you want to remove this stale example file, please run $0 -m${NC}"

            if [ "$DO_MOVE" = "true" ]; then
                # Ensure target dir exists
                mkdir -p "$old_dir_with_timestamp"
                # Move file
                mv "$stale_example_path" "$tgt_path"
                echo -e "${GREEN}Moved: $stale_example_path -> $tgt_path${NC}"
            fi
        fi
    done
}

########################################
# Main
########################################
main() {
    local do_move=${1:-false}

    echo "Using SRC_DIR: $SRC_DIR"
    echo "Using EXAMPLES_DIR: $EXAMPLES_DIR"
    echo ""
    echo "Note: This creates placeholder example files for each source module."
    echo "Only important modules need actual example implementations."
    echo ""

    # Create examples/gpac directory if it doesn't exist
    mkdir -p "$EXAMPLES_DIR"

    # # Only create examples for key modules (not every single source file)
    # local KEY_MODULES=(
    #     "_PAC.py"
    #     "_BandPassFilter.py"
    #     "_Hilbert.py"
    #     "_ModulationIndex.py"
    #     "_SyntheticDataGenerator.py"
    #     "_Profiler.py"
    # )

    # # Process each key module
    # for module in "${KEY_MODULES[@]}"; do
    #     find_files "$SRC_DIR" f "$module" | while read -r src_file; do
    #         # Skip if in subdirectory we don't want examples for
    #         [[ "$src_file" =~ /PackageHandlers/ ]] && continue

    #         # derive relative path and parts
    #         rel="${src_file#$SRC_DIR/}"
    #         rel_dir=$(dirname "$rel")
    #         src_base=$(basename "$rel")

    #         # ensure example subdir exists
    #         examples_dir="$EXAMPLES_DIR/$rel_dir"
    #         mkdir -p "$examples_dir"

    #         # build correct example file path
    #         # Convert _ModuleName.py to example_ModuleName.py
    #         example_base="example${src_base}"
    #         example_file="$examples_dir/$example_base"

    #         # Process each file
    #         update_example_file "$example_file" "$src_file"
    #     done
    # done

    find_files "$SRC_DIR" f "*.py" | while read -r src_file; do
        # Skip __init__.py files
        [[ "$(basename "$src_file")" == "__init__.py" ]] && continue

        # Skip if in subdirectory we don't want examples for
        [[ "$src_file" =~ /PackageHandlers/ ]] && continue

        # derive relative path and parts
        rel="${src_file#$SRC_DIR/}"
        rel_dir=$(dirname "$rel")
        src_base=$(basename "$rel")

        # ensure example subdir exists
        examples_dir="$EXAMPLES_DIR/$rel_dir"
        mkdir -p "$examples_dir"

        # build correct example file path
        # Convert _ModuleName.py to example_ModuleName.py
        example_base="example_${src_base}"
        example_file="$examples_dir/$example_base"

        # Process each file
        update_example_file "$example_file" "$src_file"
    done

    # Also create general examples in the root examples directory
    echo ""
    echo "Creating/checking general examples..."

    # These are already created, just check they exist
    local GENERAL_EXAMPLES=(
        "example_pac_analysis.py"
        "example_bandpass_filter.py"
        "example_profiler.py"
    )

    for example in "${GENERAL_EXAMPLES[@]}"; do
        if [ -f "${THIS_DIR}/$example" ]; then
            echo_success "Found: ${THIS_DIR}/$example"
        else
            echo_warning "Missing: ${THIS_DIR}/$example"
        fi
    done

    # Clean up stale files
    move_stale_example_files_to_old

    # Show structure
    echo ""
    echo "Examples structure:"
    tree "$THIS_DIR" -I "outputs|__pycache__|*.pyc|.old*" 2>&1 | tee -a "$LOG_PATH"
}

main "$@"
cd $ORIG_DIR

# EOF