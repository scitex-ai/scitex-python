#!/bin/bash
# -*- coding: utf-8 -*-
# Timestamp: "2025-12-13 (ywatanabe)"
# File: ./examples/plt/run_demo_plots.sh

THIS_DIR="$(cd $(dirname ${BASH_SOURCE[0]}) && pwd)"
LOG_PATH="$THIS_DIR/.$(basename $0).log"
echo > "$LOG_PATH"

main() {
    echo "Running SciTeX plotting examples..."
    echo "==================================="

    echo "[1/3] API Layers (stx_*, sns_*, mpl_*)..."
    python "$THIS_DIR/api_layers.py"

    echo "[2/3] Style Configuration..."
    python "$THIS_DIR/style_config.py"

    echo "[3/3] PLTZ Format..."
    python "$THIS_DIR/pltz.py"

    echo ""
    echo "Outputs:"
    ls -d "$THIS_DIR"/*_out 2>/dev/null
}

main "$@" | tee -a "$LOG_PATH" 2>&1

# EOF
