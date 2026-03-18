#!/bin/bash
# -*- coding: utf-8 -*-
# Timestamp: "2025-06-01 06:11:57 (ywatanabe)"
# File: ./.claude/to_claude/bin/python/black_all.sh

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

find . -type f -name "*.py" \
    -not -path "*/\.*" \
    -not -path "*/build/*" \
    -not -path "*/dist/*" \
    -not -path "*/__pycache__/*" \
    -not -path "*/node_modules/*" \
    -not -path "*/venv/*" \
    -not -path "*/.venv/*" \
    -not -path "*/env/*" \
    -not -path "*/.env/*" \
    -not -path "*/.env-*/*" \
    -not -path "*/site-packages/*" \
    -not -path "*/.git/*" \
    -not -path "*/.tox/*" \
    -not -path "*/.eggs/*" \
    -not -path "*/*.egg-info/*" \
    -print0 | xargs -0 -r black

# EOF
