#!/bin/bash
# Timestamp: "2026-03-04 (ywatanabe)"
# File: examples/scitex/clew/multi_parent/00_run_all.sh

# ==============================================================================
# SciTeX Clew - Multi-Parent DAG Demo
# ==============================================================================
#
# Demonstrates multi-parent DAG tracking and verification.
# Pipeline has diamond-shaped dependencies with 3-parent and 2-parent merges.
#
# Usage:
#   ./00_run_all.sh
#   ./00_run_all.sh --clean
#   ./00_run_all.sh --help
#
# ==============================================================================

set -e

THIS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOG_PATH="$THIS_DIR/.$(basename "$0").log"
echo >"$LOG_PATH"

# Colors
GRAY='\033[0;90m'
GREEN='\033[0;32m'
BLUE='\033[0;94m'
NC='\033[0m'

log() { echo -e "$1" | tee -a "$LOG_PATH"; }
echo_info() { log "${GRAY}INFO: $1${NC}"; }
echo_success() { log "${GREEN}SUCC: $1${NC}"; }
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
log "SciTeX Clew - Multi-Parent DAG Demo"
log "============================================================"
echo_info "Log file: $LOG_PATH"

if [ "$CLEAN" = true ]; then
    log ""
    echo_info "Cleaning output directories..."
    rm -rf ./*_out/
    echo_success "Done."
fi

# Sources (can run in parallel conceptually, but sequential for simplicity)
log ""
echo_step "1/8" "Generate subjects"
echo_line
python 01_generate_subjects.py 2>&1 | tee -a "$LOG_PATH"

log ""
echo_step "2/8" "Generate stimuli"
echo_line
python 02_generate_stimuli.py 2>&1 | tee -a "$LOG_PATH"

# Covariates must run before experiment (03 depends on 04)
log ""
echo_step "3/8" "Load covariates"
echo_line
python 04_load_covariates.py 2>&1 | tee -a "$LOG_PATH"

# 3-parent merge: subjects + stimuli + covariates
log ""
echo_step "4/8" "Run experiment (3-parent merge)"
echo_line
python 03_run_experiment.py 2>&1 | tee -a "$LOG_PATH"

# Parallel analysis branches
log ""
echo_step "5/8" "Analyze behavior"
echo_line
python 05_analyze_behavior.py 2>&1 | tee -a "$LOG_PATH"

log ""
echo_step "6/8" "Analyze neural (2-parent: raw_data + covariates)"
echo_line
python 06_analyze_neural.py 2>&1 | tee -a "$LOG_PATH"

# 2-parent merge: behavior + neural
log ""
echo_step "7/8" "Merge results (2-parent merge)"
echo_line
python 07_merge_results.py 2>&1 | tee -a "$LOG_PATH"

log ""
echo_step "8/8" "Make figures"
echo_line
python 08_make_figures.py 2>&1 | tee -a "$LOG_PATH"

log ""
log "============================================================"
echo_success "Pipeline complete! Now demonstrating DAG verification..."
log "============================================================"

# DAG verification demo
log ""
echo_step "Demo" "Multi-parent DAG verification + claims + rendering"
python 09_verify_dag.py 2>&1 | tee -a "$LOG_PATH"

log ""
log "============================================================"
echo_success "Multi-parent DAG demo complete!"
log "============================================================"
log ""
log "View DAG visualization:"
log "  file://$THIS_DIR/09_verify_dag_out/dag.html"
log ""
log "CLI commands:"
log "  scitex clew status"
log "  scitex clew dag 08_make_figures_out/figure1.png 08_make_figures_out/figure2.png"
log "  scitex clew render dag.html -f 08_make_figures_out/figure1.png -f 08_make_figures_out/figure2.png"
log ""
echo_success "Log saved to: $LOG_PATH"

# EOF
