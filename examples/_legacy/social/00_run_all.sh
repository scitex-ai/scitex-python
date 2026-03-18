#!/bin/bash
# -*- coding: utf-8 -*-
# Timestamp: 2026-01-22
# File: examples/social/00_run_all.sh
# Description: Run all social media examples

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "=== Running scitex.social examples ==="
echo

for script in "$SCRIPT_DIR"/[0-9][0-9]_*.py; do
    if [[ -f "$script" ]]; then
        echo ">>> Running: $(basename "$script")"
        python3 "$script"
        echo
    fi
done

echo "=== All examples completed ==="

# EOF
