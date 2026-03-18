#!/bin/bash
# -*- coding: utf-8 -*-
# Timestamp: "2025-05-11 13:30:54 (ywatanabe)"
# File: ./.claude/scripts/rename.sh

THIS_DIR="$(cd $(dirname ${BASH_SOURCE[0]}) && pwd)"
LOG_PATH="$THIS_DIR/.$(basename $0).log"
echo > "$LOG_PATH"

GREEN='\033[0;32m'
YELLOW='\033[0;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color
# ---------------------------------------

# Function to display usage information
show_usage() {
    echo "Usage: $0 [options] <search_pattern> <replacement> [directory]"
    echo ""
    echo "Options:"
    echo "  -h, --help             Show this help message"
    echo "  -n, --no-dry-run       Actually perform the replacements (default is dry run)"
    echo ""
    echo "Arguments:"
    echo "  <search_pattern>       Regular expression pattern to search for"
    echo "  <replacement>          String to replace matches with"
    echo "  [directory]            Target directory (default: current directory)"
    echo ""
    echo "Examples:"
    echo "  $0 'foo' 'bar'                  # Dry run replacing 'foo' with 'bar' in current dir"
    echo "  $0 -n 'foo' 'bar' /path/to/dir  # Replace 'foo' with 'bar' in specified dir"
}

# Parse command line arguments
no_dry_run=false
search_pattern=""
replacement=""
target_dir="."

while [[ $# -gt 0 ]]; do
    case "$1" in
        -h|--help)
            show_usage
            exit 0
            ;;
        -n|--no-dry-run)
            no_dry_run=true
            shift
            ;;
        -*)
            echo "Error: Unknown option: $1"
            show_usage
            exit 1
            ;;
        *)
            # Positional arguments
            if [ -z "$search_pattern" ]; then
                search_pattern="$1"
            elif [ -z "$replacement" ]; then
                replacement="$1"
            elif [ "$target_dir" = "." ]; then
                target_dir="$1"
            else
                echo "Error: Too many arguments"
                show_usage
                exit 1
            fi
            shift
            ;;
    esac
done

# Check if required arguments are provided
if [ -z "$search_pattern" ] || [ -z "$replacement" ]; then
    echo "Error: Missing required arguments"
    show_usage
    exit 1
fi

# Set dry run mode (dry run is default)
dry_run=true
if $no_dry_run; then
    dry_run=false
    echo "LIVE MODE: Changes will be applied"
else
    echo "DRY RUN MODE: No changes will be made (use -n to apply changes)"
fi

# Function to replace content in files
replace_in_files() {
    echo "Replacing content in files..."
    find "$target_dir" -type f -not -path "*/\.*" -exec grep -l "$search_pattern" {} \; | while read file_path; do
        echo "Processing file: $file_path"
        if $dry_run; then
            # Show what would be replaced
            grep --color=always -n "$search_pattern" "$file_path" | head -5
            match_count=$(grep -c "$search_pattern" "$file_path")
            if [ $match_count -gt 5 ]; then
                echo "... ($match_count matches found, showing first 5)"
            fi
        else
            # Actually do the replacement
            sed -i "s/$search_pattern/$replacement/g" "$file_path"
        fi
    done
}

# Function to rename files and directories
rename_files_and_dirs() {
    echo "Renaming files and directories..."

    # Process files/dirs from deepest to root level to avoid path issues
    find "$target_dir" -depth -not -path "*/\.*" | while read item_path; do
        # Get the directory and filename parts
        dir_part=$(dirname "$item_path")
        base_part=$(basename "$item_path")

        # Check if the file/dir name matches the pattern
        if [[ "$base_part" =~ $search_pattern ]]; then
            # Create the new name
            new_name=$(echo "$base_part" | sed "s/$search_pattern/$replacement/g")
            new_path="$dir_part/$new_name"

            # Rename or show what would be renamed
            if [ "$base_part" != "$new_name" ]; then
                echo "Renaming: $item_path → $new_path"
                if ! $dry_run; then
                    mv "$item_path" "$new_path"
                fi
            fi
        fi
    done
}

# Execute the functions
replace_in_files
rename_files_and_dirs

if $dry_run; then
    echo "Dry run completed. No actual changes were made."
else
    echo "Replacement completed successfully."
fi

# EOF
