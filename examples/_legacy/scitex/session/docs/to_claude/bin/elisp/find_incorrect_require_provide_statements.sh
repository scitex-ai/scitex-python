#!/bin/bash
# -*- coding: utf-8 -*-
# Timestamp: "2025-05-12 13:19:08 (ywatanabe)"
# File: ./.claude/tools/find_incorrect_require_provide_statements.sh

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

REPOSITORY_HOME="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"

# Script to find incorrect require and provide statements in Emacs Lisp files

# Function to log messages
log_message() {
    local level=$1
    local message=$2
    local color=$NC

    case $level in
        "INFO") color=$GREEN ;;
        "WARNING") color=$YELLOW ;;
        "ERROR") color=$RED ;;
    esac

    echo -e "${color}[$level] $message${NC}"
    echo "[$level] $message" >> "$LOG_PATH"
}

# Function to check if provide statement matches filename
check_provide_statement() {
    local file_path=$1
    local filename=$(basename "$file_path" .el)
    local provide_statements=$(grep -o "(provide '[^)]*)" "$file_path" | sed "s/(provide '//g" | sed "s/)//g")

    if [ -z "$provide_statements" ]; then
        log_message "ERROR" "$file_path:\nNo provide statement"
        return 1
    fi

    local main_provide=$(echo "$provide_statements" | head -1)
    if [[ "$main_provide" != "$filename" ]]; then
        log_message "ERROR" "$file_path\nProvide statement '$main_provide' doesn't match filename '$filename'"
        return 1
    fi

    # Check for provides with slashes
    if echo "$provide_statements" | grep -q "/"; then
        log_message "WARNING" "$file_path\nProvide statement contains slash: $(echo "$provide_statements" | grep "/")"
    fi

    return 0
}

# Function to check require statements
check_require_statements() {
    local file_path=$1
    local require_statements=$(grep -o "(require '[^)]*)" "$file_path" | sed "s/(require '//g" | sed "s/)//g")

    if [ -z "$require_statements" ]; then
        return 0
    fi

    # Check for requires with slashes
    if echo "$require_statements" | grep -q "/"; then
        log_message "WARNING" "Require statement contains slash in $file_path: $(echo "$require_statements" | grep "/")"
    fi

    return 0
}

# Main function
main() {
    local elisp_files

    # Find all Emacs Lisp files in the repository
    # elisp_files=$(find "$REPOSITORY_HOME" -name "*.el" -type f -not -path "*/\.*")
    elisp_files=$(find $REPOSITORY_HOME -name "*.el" -type f | grep -v ".old")

    log_message "INFO" "Checking $(echo "$elisp_files" | wc -l) Emacs Lisp files"

    local errors=0
    local warnings=0

    for file in $elisp_files; do
        check_provide_statement "$file" || ((errors++))
        check_require_statements "$file" || ((warnings++))
    done

    if [ $errors -eq 0 ] && [ $warnings -eq 0 ]; then
        log_message "INFO" "All files passed validation"
    else
        log_message "INFO" "Found $errors errors and $warnings warnings. See $LOG_PATH for details."
    fi
}

# Execute main function
main "$@"

# EOF
