#!/bin/bash
# -*- coding: utf-8 -*-
# Timestamp: "2025-05-12 22:48:10 (ywatanabe)"
# File: ./.claude/tools/sync_elisp_tdd.sh

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
REPO_ROOT=$(git rev-parse --show-toplevel 2>/dev/null || realpath "$(dirname "$0")/..")

# Set up colors for terminal output

########################################
# Usage & Argument Parser
########################################
# Default Values
DO_MOVE=false
PACKAGE_NAME=""
SRC_DIR="$REPO_ROOT/src"
TESTS_DIR="$REPO_ROOT/tests"

usage() {
    echo "Usage: $0 [options]"
    echo
    echo "Synchronizes Elisp project structure using test-driven development approach."
    echo
    echo "Options:"
    echo "  -p, --package NAME         Specify package name (required)"
    echo "  -m, --move-stale-source    Move stale source files to .old directory (default: $DO_MOVE)"
    echo "  -s, --source DIR           Specify custom source directory (default: $SRC_DIR)"
    echo "  -t, --tests DIR            Specify custom tests directory (default: $TESTS_DIR)"
    echo "  -h, --help                 Display this help message"
    echo
    echo "Example:"
    echo "  $0 --package my-awesome-package --move"
    exit 1
}

while [[ $# -gt 0 ]]; do
    case $1 in
        -p|--package)
            PACKAGE_NAME="$2"
            shift 2
            ;;
        -m|--move)
            DO_MOVE=true
            shift
            ;;
        -s|--source)
            SRC_DIR="$2"
            shift 2
            ;;
        -t|--tests)
            TESTS_DIR="$2"
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

# Validate required arguments
if [ -z "$PACKAGE_NAME" ]; then
    echo "Error: Package name is required"
    usage
fi

########################################
# TDD Structure Functions
########################################
prepare_basic_structure() {
    # Ensure the directories exist
    mkdir -p "$TESTS_DIR"
    mkdir -p "$SRC_DIR"

    # Create main test file if it doesn't exist
    if [ ! -f "$TESTS_DIR/test-${PACKAGE_NAME}.el" ]; then
        echo -e "${YELLOW}Creating main test file: $TESTS_DIR/test-${PACKAGE_NAME}.el${NC}"
        cat > "$TESTS_DIR/test-${PACKAGE_NAME}.el" << EOL
;;; test-${PACKAGE_NAME}.el --- Tests for ${PACKAGE_NAME} package

;;; Commentary:
;; Main tests for ${PACKAGE_NAME} package

;;; Code:

(require 'ert)

(ert-deftest test-${PACKAGE_NAME}-loadability ()
  "Test that ${PACKAGE_NAME} package loads correctly."
  (should (locate-library "${PACKAGE_NAME}"))
  (require '${PACKAGE_NAME})
  (should (featurep '${PACKAGE_NAME})))

;;; test-${PACKAGE_NAME}.el ends here
EOL
    fi

    # Create main package entry point based on test if it doesn't exist
    if [ ! -f "$REPO_ROOT/${PACKAGE_NAME}.el" ]; then
        echo -e "${YELLOW}Creating package entry point: $REPO_ROOT/${PACKAGE_NAME}.el${NC}"
        cat > "$REPO_ROOT/${PACKAGE_NAME}.el" << EOL
;;; ${PACKAGE_NAME}.el --- Main entry point for ${PACKAGE_NAME}

;; Author: Your Name <your.email@example.com>
;; Version: 0.1
;; Package-Requires: ((emacs "25.1"))
;; Keywords: tools
;; URL: https://github.com/yourusername/${PACKAGE_NAME}

;;; Commentary:
;; Main entry point for ${PACKAGE_NAME}

;;; Code:

;; Add src directory to load path
(add-to-list 'load-path (concat (file-name-directory
                               (or load-file-name buffer-file-name))
                              "src"))

;; Required umbrella modules
;; Will be auto-populated from test requirements

(provide '${PACKAGE_NAME})

;;; ${PACKAGE_NAME}.el ends here
EOL
    fi
}

extract_test_function_definitions() {
    local test_file=$1
    local temp_file=$(mktemp)

    # Extract all ert-deftest definitions from test file
    grep -n "ert-deftest" "$test_file" | while read -r line; do
        line_num=$(echo "$line" | cut -d':' -f1)
        function_name=$(echo "$line" | sed -n 's/.*ert-deftest \([^ ]*\).*/\1/p')

        # Extract function being tested (remove test- prefix and -specific-test-name suffix)
        if [[ "$function_name" =~ ^test-(.+)-[^-]+ ]]; then
            tested_func="${BASH_REMATCH[1]}"
            echo "$tested_func"
        fi
    done | sort | uniq > "$temp_file"

    cat "$temp_file"
    rm "$temp_file"
}

parse_umbrella_from_testfile() {
    local test_file=$1
    local basename=$(basename "$test_file" .el)

    # If it's test-umbrella-xxx-yyy.el format
    if [[ "$basename" =~ ^test-umbrella-([^-]+)-(.+)$ ]]; then
        umbrella_name="umbrella-${BASH_REMATCH[1]}"
        component_name="${BASH_REMATCH[2]}"
        echo "$umbrella_name"
    fi
}

parse_component_from_testfile() {
    local test_file=$1
    local basename=$(basename "$test_file" .el)

    # If it's test-umbrella-xxx-yyy.el format
    if [[ "$basename" =~ ^test-umbrella-([^-]+)-(.+)$ ]]; then
        umbrella_name="umbrella-${BASH_REMATCH[1]}"
        component_name="${BASH_REMATCH[2]}"
        echo "$component_name"
    fi
}

create_source_from_test() {
    local test_file=$1
    local basename=$(basename "$test_file" .el)

    # Skip if it's the main package test
    if [ "$basename" == "test-$PACKAGE_NAME" ]; then
        return
    fi

    # Skip if it's an umbrella test integrator
    if [[ "$basename" =~ ^test-umbrella-[^-]+$ ]]; then
        return
    fi

    # Parse umbrella and component names
    local umbrella_name=$(parse_umbrella_from_testfile "$test_file")
    local component_name=$(parse_component_from_testfile "$test_file")

    if [ -z "$umbrella_name" ] || [ -z "$component_name" ]; then
        echo -e "${RED}Cannot parse umbrella/component from: $basename${NC}"
        return
    fi

    # Ensure umbrella directory exists
    mkdir -p "$SRC_DIR/$umbrella_name"

    # Create umbrella integrator if missing
    if [ ! -f "$SRC_DIR/$umbrella_name/$umbrella_name.el" ]; then
        echo -e "${YELLOW}Creating umbrella integrator: $SRC_DIR/$umbrella_name/$umbrella_name.el${NC}"
        cat > "$SRC_DIR/$umbrella_name/$umbrella_name.el" << EOL
;;; $umbrella_name.el --- Integrator for $umbrella_name component

;;; Commentary:
;; Integrator for $umbrella_name component

;;; Code:

;; Required components
;; Will be auto-populated from test requirements

(provide '$umbrella_name)

;;; $umbrella_name.el ends here
EOL
    fi

    # Determine component source file path
    local component_full_name="${umbrella_name}-${component_name}"
    local component_src_file="$SRC_DIR/$umbrella_name/$component_full_name.el"

    # Extract function definitions from test file
    local functions=$(extract_test_function_definitions "$test_file")

    # If source file doesn't exist or we're supposed to update it
    if [ ! -f "$component_src_file" ]; then
        echo -e "${YELLOW}Creating component source from test: $component_src_file${NC}"

        # Create function stubs based on test requirements
        cat > "$component_src_file" << EOL
;;; $component_full_name.el --- $component_name component for $umbrella_name

;;; Commentary:
;; Implementation for $component_name component
;; Generated from test file: $test_file

;;; Code:

;; Functions required by tests:
EOL

        # Add function stubs based on tested functions
        for func in $functions; do
            cat >> "$component_src_file" << EOL

(defun $func ()
  "Generated stub for $func required by tests."
  nil)
EOL
        done

        # Add standard footer
        cat >> "$component_src_file" << EOL

(provide '$component_full_name)

;;; $component_full_name.el ends here
EOL
    fi
}

create_umbrella_test_integrator() {
    local umbrella_name=$1
    local test_umbrella_dir="$TESTS_DIR/test-$umbrella_name"
    local test_umbrella_file="$test_umbrella_dir/test-$umbrella_name.el"

    # Create test umbrella directory if needed
    mkdir -p "$test_umbrella_dir"

    # Create umbrella test integrator if missing
    if [ ! -f "$test_umbrella_file" ]; then
        echo -e "${YELLOW}Creating umbrella test integrator: $test_umbrella_file${NC}"
        cat > "$test_umbrella_file" << EOL
;;; test-$umbrella_name.el --- Tests for $umbrella_name integrator

;;; Commentary:
;; Tests for $umbrella_name integrator

;;; Code:

(require 'ert)
(require '$umbrella_name)

(ert-deftest test-$umbrella_name-loadability ()
  "Test that $umbrella_name module loads correctly."
  (should (featurep '$umbrella_name)))

;;; test-$umbrella_name.el ends here
EOL
    fi
}

update_umbrella_from_tests() {
    local umbrella_name=$1
    local umbrella_file="$SRC_DIR/$umbrella_name/$umbrella_name.el"
    local test_umbrella_dir="$TESTS_DIR/test-$umbrella_name"

    # Skip if umbrella file doesn't exist
    if [ ! -f "$umbrella_file" ]; then
        return
    fi

    # Find all component test files
    local components=()
    for test_file in "$test_umbrella_dir/test-$umbrella_name-"*.el; do
        if [ -f "$test_file" ]; then
            component_basename=$(basename "$test_file" .el)
            component_name=${component_basename#test-$umbrella_name-}
            component_full_name="${umbrella_name}-${component_name}"
            components+=("$component_full_name")
        fi
    done

    # Create new umbrella file content with proper requires
    local temp_file=$(mktemp)
    awk -v components="${components[*]}" '
        /;; Required components/ {
            print $0
            if (components != "") {
                split(components, comp_array, " ")
                for (ii in comp_array) {
                    print "(require \047" comp_array[ii] ")"
                }
            } else {
                print ";; No components found in tests"
            }
            in_require_section = 1
            next
        }
        /\(require / {
            if (in_require_section) next
        }
        /\(provide / {
            in_require_section = 0
            print ""
            print $0
            next
        }
        {
            if (!in_require_section) print $0
        }
    ' "$umbrella_file" > "$temp_file"

    # Replace original file if content is different
    if ! cmp -s "$temp_file" "$umbrella_file"; then
        echo -e "${GREEN}Updating umbrella integrator: $umbrella_file${NC}"
        mv "$temp_file" "$umbrella_file"
    else
        rm "$temp_file"
    fi
}

update_main_package_from_tests() {
    local package_file="$REPO_ROOT/${PACKAGE_NAME}.el"

    # Skip if package file doesn't exist
    if [ ! -f "$package_file" ]; then
        return
    fi

    # Find all umbrella test directories
    local umbrellas=()
    for test_umbrella_dir in "$TESTS_DIR"/test-umbrella-*; do
        if [ -d "$test_umbrella_dir" ]; then
            umbrella_basename=$(basename "$test_umbrella_dir")
            umbrella_name=${umbrella_basename#test-}
            umbrellas+=("$umbrella_name")
        fi
    done

    # Create new package file content with proper requires
    local temp_file=$(mktemp)
    awk -v umbrellas="${umbrellas[*]}" '
        /;; Required umbrella modules/ {
            print $0
            if (umbrellas != "") {
                split(umbrellas, umb_array, " ")
                for (ii in umb_array) {
                    print "(require \047" umb_array[ii] ")"
                }
            } else {
                print ";; No umbrella modules found in tests"
            }
            in_require_section = 1
            next
        }
        /\(require / {
            if (in_require_section) next
        }
        /\(provide / {
            in_require_section = 0
            print ""
            print $0
            next
        }
        {
            if (!in_require_section) print $0
        }
    ' "$package_file" > "$temp_file"

    # Replace original file if content is different
    if ! cmp -s "$temp_file" "$package_file"; then
        echo -e "${GREEN}Updating package entry point: $package_file${NC}"
        mv "$temp_file" "$package_file"
    else
        rm "$temp_file"
    fi
}

move_stale_source_files() {
    if [ "$DO_MOVE" != "true" ]; then
        return
    fi

    local timestamp="$(date +%Y%m%d_%H%M%S)"

    # Check for source files without corresponding test files
    find "$SRC_DIR" -type f -name "*.el" | while read src_file; do
        local src_basename=$(basename "$src_file" .el)
        local src_rel_path="${src_file#$SRC_DIR/}"

        # Skip umbrella integrators
        if [[ "$src_basename" =~ ^umbrella-[^-]+$ ]]; then
            continue
        fi

        # Determine corresponding test file
        local test_file=""
        if [[ "$src_basename" =~ ^(umbrella-[^-]+)-(.+)$ ]]; then
            umbrella=${BASH_REMATCH[1]}
            component=${BASH_REMATCH[2]}
            test_file="$TESTS_DIR/test-$umbrella/test-$src_basename.el"
        fi

        # If no test file, move to .old directory
        if [ -n "$test_file" ] && [ ! -f "$test_file" ]; then
            old_dir=$(dirname "$src_file")/.old-$timestamp
            mkdir -p "$old_dir"
            echo -e "${RED}Moving stale source file: $src_file -> $old_dir/$(basename "$src_file")${NC}"
            mv "$src_file" "$old_dir/"
        fi
    done

    # Check for empty umbrella directories and clean them up
    find "$SRC_DIR" -type d -name "umbrella-*" | while read umbrella_dir; do
        # If only contains .old directories or the umbrella integrator
        local file_count=$(find "$umbrella_dir" -type f -not -path "*.old*" | wc -l)
        if [ "$file_count" -le 1 ]; then
            # Check if there's only the integrator file
            local integrator=$(basename "$umbrella_dir").el
            if [ -f "$umbrella_dir/$integrator" ] && [ "$file_count" -eq 1 ]; then
                old_dir="$umbrella_dir/.old-$timestamp"
                mkdir -p "$old_dir"
                echo -e "${RED}Moving stale umbrella integrator: $umbrella_dir/$integrator -> $old_dir/$integrator${NC}"
                mv "$umbrella_dir/$integrator" "$old_dir/"
            fi
        fi
    done
}

########################################
# Main
########################################
main() {
    echo "Synchronizing Elisp project structure (TDD approach) for: $PACKAGE_NAME"
    echo "Source directory: $SRC_DIR"
    echo "Tests directory: $TESTS_DIR"

    # Prepare basic structure
    prepare_basic_structure

    # Create example test structure if none exists
    if [ ! -d "$TESTS_DIR/test-umbrella-xxx" ] && [ ! -d "$TESTS_DIR/test-umbrella-yyy" ]; then
        echo -e "${YELLOW}Creating example test structure${NC}"

        # Create test directories
        mkdir -p "$TESTS_DIR/test-umbrella-xxx"
        mkdir -p "$TESTS_DIR/test-umbrella-yyy"

        # Create umbrella test integrators
        create_umbrella_test_integrator "umbrella-xxx"
        create_umbrella_test_integrator "umbrella-yyy"

        # Create component test files
        cat > "$TESTS_DIR/test-umbrella-xxx/test-umbrella-xxx-aaa.el" << EOL
;;; test-umbrella-xxx-aaa.el --- Tests for aaa component

;;; Commentary:
;; Tests for aaa component

;;; Code:

(require 'ert)

(ert-deftest test-umbrella-xxx-aaa-function-1 ()
  "Test example function 1."
  (should (fboundp 'umbrella-xxx-aaa-function-1))
  (should (equal "result" (umbrella-xxx-aaa-function-1))))

(ert-deftest test-umbrella-xxx-aaa-function-2 ()
  "Test example function 2."
  (should (fboundp 'umbrella-xxx-aaa-function-2))
  (should (numberp (umbrella-xxx-aaa-function-2))))

;;; test-umbrella-xxx-aaa.el ends here
EOL

        cat > "$TESTS_DIR/test-umbrella-xxx/test-umbrella-xxx-bbb.el" << EOL
;;; test-umbrella-xxx-bbb.el --- Tests for bbb component

;;; Commentary:
;; Tests for bbb component

;;; Code:

(require 'ert)

(ert-deftest test-umbrella-xxx-bbb-function-1 ()
  "Test example function 1."
  (should (fboundp 'umbrella-xxx-bbb-function-1))
  (should (listp (umbrella-xxx-bbb-function-1))))

;;; test-umbrella-xxx-bbb.el ends here
EOL

        cat > "$TESTS_DIR/test-umbrella-yyy/test-umbrella-yyy-ccc.el" << EOL
;;; test-umbrella-yyy-ccc.el --- Tests for ccc component

;;; Commentary:
;; Tests for ccc component

;;; Code:

(require 'ert)

(ert-deftest test-umbrella-yyy-ccc-function-1 ()
  "Test example function 1."
  (should (fboundp 'umbrella-yyy-ccc-function-1))
  (should (string-or-null-p (umbrella-yyy-ccc-function-1))))

;;; test-umbrella-yyy-ccc.el ends here
EOL

        cat > "$TESTS_DIR/test-umbrella-yyy/test-umbrella-yyy-ddd.el" << EOL
;;; test-umbrella-yyy-ddd.el --- Tests for ddd component

;;; Commentary:
;; Tests for ddd component

;;; Code:

(require 'ert)

(ert-deftest test-umbrella-yyy-ddd-function-1 ()
  "Test example function 1."
  (should (fboundp 'umbrella-yyy-ddd-function-1))
  (should (functionp (umbrella-yyy-ddd-function-1))))

;;; test-umbrella-yyy-ddd.el ends here
EOL
    fi

    # Process all test directories to create umbrella integrators
    for test_umbrella_dir in "$TESTS_DIR"/test-umbrella-*; do
        if [ -d "$test_umbrella_dir" ]; then
            umbrella_basename=$(basename "$test_umbrella_dir")
            umbrella_name=${umbrella_basename#test-}
            create_umbrella_test_integrator "$umbrella_name"
        fi
    done

    # Process all test files to create source files
    find "$TESTS_DIR" -name "test-*.el" | while read test_file; do
        create_source_from_test "$test_file"
    done

    # Update umbrella integrators from test requirements
    for umbrella_dir in "$SRC_DIR"/umbrella-*; do
        if [ -d "$umbrella_dir" ]; then
            umbrella_basename=$(basename "$umbrella_dir")
            update_umbrella_from_tests "$umbrella_basename"
        fi
    done

    # Update main package from test requirements
    update_main_package_from_tests

    # Clean up stale source files
    move_stale_source_files

    echo -e "${GREEN}Elisp project structure synchronized successfully!${NC}"
    echo "See test directory structure:"
    tree "$TESTS_DIR" -I "*.elc|*~|.git" | head -n 30
    echo "See source directory structure:"
    tree "$SRC_DIR" -I "*.elc|*~|.git" | head -n 30

    # Log full structure
    tree "$REPO_ROOT" -I "*.elc|*~|.git" 2>&1 >> "$LOG_PATH"
}

main "$@"

# EOF
