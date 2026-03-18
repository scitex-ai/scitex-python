#!/bin/bash
# -*- coding: utf-8 -*-
# Timestamp: "2025-02-15 02:01:51 (ywatanabe)"
# File: /home/ywatanabe/proj/example-scitex-project/scripts/mnist/main.sh

THIS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOG_PATH="$0.log"
touch "$LOG_PATH"

cleanup() {
    rm -rf ./data/*
    rm -rf ./scripts/mnist/*_out
}

main() {
    ./scripts/mnist/download.py
    ./scripts/mnist/plot_digits.py
    ./scripts/mnist/plot_umap_space.py
    ./scripts/mnist/clf_svm.py
    ./scripts/mnist/clf_svm_plot_conf_mat.py
}

cleanup
main "$@" 2>&1 | tee "$LOG_PATH"

# EOF
