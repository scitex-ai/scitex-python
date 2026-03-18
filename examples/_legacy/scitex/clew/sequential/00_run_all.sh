#!/bin/bash
# -*- coding: utf-8 -*-
# Timestamp: "2026-02-01 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex-python/examples/scitex/verify/00_run_all.sh

# ==============================================================================
# SciTeX Verify Module - Run All Examples
# ==============================================================================
#
# Demonstrates verification DAG with multi-script pipeline.
# Shows cache (✓), rerun (✓✓), and failed (✗) verification states.
#
# Usage:
#   ./00_run_all.sh
#   ./00_run_all.sh --clean
#
# ==============================================================================

set -e

THIS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOG_PATH="$THIS_DIR/.$(basename "$0").log"
echo >"$LOG_PATH"

# Colors
GRAY='\033[0;90m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
RED='\033[0;31m'
BLUE='\033[0;94m'
NC='\033[0m' # No Color

# Logging functions (output to both console and log file)
log() { echo -e "$1" | tee -a "$LOG_PATH"; }
echo_info() { log "${GRAY}INFO: $1${NC}"; }
echo_success() { log "${GREEN}SUCC: $1${NC}"; }
echo_warning() { log "${YELLOW}WARN: $1${NC}"; }
echo_error() { log "${RED}ERRO: $1${NC}"; }
echo_header() { log "${BLUE}=== $1 ===${NC}"; }
echo_step() { log "${BLUE}[$1] $2${NC}"; }
echo_line() { log "------------------------------------------------------------"; }

cd "$THIS_DIR"

# Parse arguments
CLEAN=false
for arg in "$@"; do
    case $arg in
    --clean | -c)
        CLEAN=true
        shift
        ;;
    --help | -h)
        echo "Usage: $0 [--clean]"
        echo ""
        echo "Options:"
        echo "  --clean, -c  Clean output directories before running"
        echo "  --help, -h   Show this help message"
        echo ""
        echo "Log file: $LOG_PATH"
        exit 0
        ;;
    esac
done

log ""
log "============================================================"
log "SciTeX Verify Module - Multi-Script Pipeline Demo"
log "============================================================"
echo_info "Log file: $LOG_PATH"

# Clean output directories if requested
if [ "$CLEAN" = true ]; then
    log ""
    echo_info "Cleaning output directories..."
    rm -rf ./*_out/
    echo_success "Done."
fi

# Run pipeline
log ""
echo_step "1/8" "Source A (with config)"
echo_line
python 01_source_a.py 2>&1 | tee -a "$LOG_PATH"

log ""
echo_step "2/8" "Preprocess A"
echo_line
python 02_preprocess_a.py 2>&1 | tee -a "$LOG_PATH"

log ""
echo_step "3/8" "Source B"
echo_line
python 03_source_b.py 2>&1 | tee -a "$LOG_PATH"

log ""
echo_step "4/8" "Preprocess B"
echo_line
python 04_preprocess_b.py 2>&1 | tee -a "$LOG_PATH"

log ""
echo_step "5/8" "Source C"
echo_line
python 05_source_c.py 2>&1 | tee -a "$LOG_PATH"

log ""
echo_step "6/8" "Preprocess C"
echo_line
python 06_preprocess_c.py 2>&1 | tee -a "$LOG_PATH"

log ""
echo_step "7/8" "Merge all branches"
echo_line
python 07_merge.py 2>&1 | tee -a "$LOG_PATH"

log ""
echo_step "8/8" "Analyze final data"
echo_line
python 08_analyze.py 2>&1 | tee -a "$LOG_PATH"

log ""
log "============================================================"
echo_success "Pipeline complete! Now demonstrating verification states..."
log "============================================================"

# Demo rerun verification (✓✓)
log ""
echo_step "Demo" "Recording rerun verification for branch A sessions..."
python 09_demo_verification.py --action=rerun 2>&1 | tee -a "$LOG_PATH"

# Demo failure (✗) by modifying clean_C.csv
log ""
echo_step "Demo" "Modifying clean_C.csv to simulate failure..."
python 09_demo_verification.py --action=break 2>&1 | tee -a "$LOG_PATH"

# Generate DAG visualization
log ""
echo_step "Demo" "Generating DAG visualization..."
python 09_demo_verification.py --action=visualize 2>&1 | tee -a "$LOG_PATH"

# Show programmatic verification API usage
log ""
echo_step "Demo" "Programmatic verification API..."
python 10_programmatic_verification.py 2>&1 | tee -a "$LOG_PATH"

log ""
log "============================================================"
echo_success "Verification states demonstrated:"
log "============================================================"
log "  ✓   Cache-verified (fast hash check)"
log "  ✓✓  Rerun-verified (re-executed script)"
log "  ✗   Failed (hash mismatch after modification)"
log ""
log "View DAG visualization:"
log "  file://$THIS_DIR/09_demo_verification_out/dag.html"
log ""
log "CLI commands:"
log "  scitex clew status     # Show changed items"
log "  scitex clew list       # List all tracked runs"
log "  scitex clew chain FILE # Trace file dependencies"
log ""
echo_success "Log saved to: $LOG_PATH"

# EOF
