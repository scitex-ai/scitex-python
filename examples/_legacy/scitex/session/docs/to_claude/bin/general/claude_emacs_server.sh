#!/bin/bash
# -*- coding: utf-8 -*-
# Timestamp: "2025-05-20 05:20:10 (ywatanabe)"
# File: ./.claude/to_claude/bin/claude_emacs_server.sh

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

THIS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOG_PATH="$THIS_DIR/.$(basename "$0").log"
# Get login name
if [ -n "$CLAUDE_ID" ]; then
    LOGIN_NAME="CLAUDE-$(echo "$CLAUDE_ID" | cut -d'-' -f1)"
else
    LOGIN_NAME="$USER"
fi
EMACS_SOCKET="/home/ywatanabe/.emacs.d/server/server"
EMACS_CLIENT="/opt/emacs-30.1/bin/emacsclient"

# Helper
# ----------------------------------------

claude_emacs_client() {
    DISPLAY=:0 && "$EMACS_CLIENT" --socket-name="$EMACS_SOCKET" "$@"
}

# Frame Management
# ----------------------------------------

claude_emacs_manage_frame() {
    # Check if emacs server is available
    if ! claude_emacs_client -e 't' &>/dev/null; then
        echo_error "Please ask the user to start emacs server by M-x server-start"
        exit 1
    fi

    # First ensure only one frame exists (if any)
    claude_emacs_client -e '(let ((frames (filtered-frame-list (lambda (f) (equal (frame-parameter f '\''name) "claude-frame")))))
                            (when (> (length frames) 1)
                              (dolist (frame (cdr frames))
                                (delete-frame frame))))'
    # Then check if we need to create a frame
    local frame_exists=$(claude_emacs_client -e '(if (filtered-frame-list (lambda (f) (equal (frame-parameter f '\''name) "claude-frame"))) "exists" "none")')
    if [[ "$frame_exists" == "none" ]]; then
        claude_emacs_client \
            --create-frame \
            --no-wait \
            --frame-parameters='((name . "claude-frame") (left . 800) (top . 100) (width . 80) (height . 35))' \
            -e '(message "Start working in dedicated frame")'
    fi
}

# Arbitrary Emacs Lisp Code
# ----------------------------------------

claude_emacs_run_progn() {
    local elisp_code="$*"

    # Check if emacs server is available
    if ! claude_emacs_client -e 't' &>/dev/null; then
        echo_error "Please start emacs server by M-x server-start"
        exit 1
    fi

    # Execute the Elisp code
    local result=$(claude_emacs_client -e "$elisp_code")
    echo "$result"
}

# Discussion
# ----------------------------------------

claude_ensure_discussion_buffer() {
    claude_emacs_client -e '(progn
      (let ((buffer (get-buffer-create "*CLAUDE-DISCUSSION*")))
        (with-current-buffer buffer
          (when (= (buffer-size) 0)
            (insert ";; CLAUDE DISCUSSION BUFFER\n")
            (insert ";; ======================\n"))
          (lisp-interaction-mode))))' >/dev/null
}

claude_discussion_send() {
    local comment="$*"
    local final_comment="[$LOGIN_NAME] $comment"
    claude_emacs_manage_frame >/dev/null
    claude_ensure_discussion_buffer >/dev/null
    claude_emacs_client \
        -e "(with-current-buffer \"*CLAUDE-DISCUSSION*\"
              (goto-char (point-max))
              (insert \"\n\n$final_comment\"))" >/dev/null
    echo_success "Message sent: $final_comment"
}


claude_discussion_read() {
    claude_emacs_manage_frame >/dev/null
    claude_ensure_discussion_buffer >/dev/null
    local raw_content=$(claude_emacs_client -e '(with-current-buffer "*CLAUDE-DISCUSSION*"
                                 (substring-no-properties (buffer-string)))')

    # Process the output to remove the 'nil' prefix and text properties
    # This extracts just the actual content string
    if [[ "$raw_content" == nil* ]]; then
        # If it starts with 'nil', remove it and parse the actual string content
        echo_success "$raw_content" | sed 's/^nil//' | grep -o '".*"' | sed 's/^"//;s/"$//'
    else
        # Otherwise just return the raw content
        echo_success "$raw_content"
    fi
}

# Usage information
usage() {
    echo "Usage: $0 [OPTIONS] [MESSAGE]"
    echo
    echo "Options:"
    echo "  -s, --send MESSAGE     Send a message to Claude discussion"
    echo "  -r, --read             Read the content of Claude discussion"
    echo "  -e, --eval CODE        Evaluate Emacs Lisp code"
    echo "  -h, --help             Display this help message"
    echo
    echo "Examples:"
    echo "  $0 -s \"Check this function\"              # Send a message explicitly"
    echo "  $0 -r                                    # Read discussion content"
    echo "  $0 -e \"(+ 2 3)\"                          # Evaluate Elisp code"
    echo
    exit 1
}


# Main function to parse arguments and execute commands
main() {
    if [[ $# -eq 0 ]]; then
        usage
        exit 1
    fi
    # Parse arguments
    while [[ $# -gt 0 ]]; do
        case "$1" in
            -s|--send)
                shift
                if [[ $# -eq 0 ]]; then
                    echo_error "Error: No message provided after -s/--send option."
                    usage
                fi
                claude_discussion_send "$*"
                exit 0
                ;;
            -r|--read)
                claude_discussion_read
                exit 0
                ;;
            -e|--eval)
                shift
                if [[ $# -eq 0 ]]; then
                    echo_error "Error: No Elisp code provided after -e/--eval option."
                    usage
                fi
                claude_emacs_run_progn "$*"
                exit 0
                ;;
            -h|--help)
                usage
                ;;
            *)
                echo_error "'$1' is not acceptable option. Please see usage."
                usage
                ;;
        esac
        shift
    done
}

# Execute main function with all arguments
main "$@" 2>&1 | tee -a "$LOG_PATH"

# EOF
