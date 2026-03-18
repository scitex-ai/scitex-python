#!/bin/bash
# -*- coding: utf-8 -*-
# Timestamp: "2025-05-15 03:49:40 (ywatanabe)"
# File: ./.claude/tools/check_parens.sh

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

check_parens() {
    local file="$1"

    # Create a minimal elisp script
    elisp_script=$(mktemp)
    cat > "$elisp_script" << 'EOF'
(require 'lisp-mode)

(defun my/check-parens-file (file)
  (with-temp-buffer
    (insert-file-contents file)
    (emacs-lisp-mode)
    (condition-case err
        (progn
          (check-parens)
          (message "Parentheses are balanced in %s" file))
      (error
       (let* ((pos (point))
              (line (line-number-at-pos))
              (col (current-column)))
         (message "Unbalanced: %s at line %d, column %d"
                 (error-message-string err) line col))))))

(my/check-parens-file (car command-line-args-left))
EOF

    # Execute the elisp script
    emacs --batch --load "$elisp_script" "$file" 2>&1
    rm -f "$elisp_script"
}

check_parens "$@"

# EOF
