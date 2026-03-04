#!/usr/bin/env python3
# Timestamp: "2026-03-04 (ywatanabe)"
# File: examples/scitex/clew/multi_parent/06_analyze_neural.py

"""Analyze neural responses with covariate correction (2-parent merge)."""

from pathlib import Path

import scitex as stx

SCRIPT_DIR = Path(__file__).parent


@stx.session
def main(
    raw_file: str = None,
    covariates_file: str = None,
    CONFIG=stx.session.INJECTED,
    logger=stx.session.INJECTED,
):
    """Analyze neural data with covariate correction (2 parents)."""
    raw_file = raw_file or str(SCRIPT_DIR / "03_run_experiment_out" / "raw_data.csv")
    covariates_file = covariates_file or str(
        SCRIPT_DIR / "04_load_covariates_out" / "covariates.csv"
    )
    logger.info("Analyzing neural responses")

    raw = stx.io.load(raw_file)
    covariates = stx.io.load(covariates_file)

    # Merge covariates and compute adjusted neural response
    merged = raw.merge(covariates[["subject_id", "score"]], on="subject_id", how="left")
    merged["adjusted_response"] = merged["neural_response"] - (merged["score"] * 0.01)

    stats = (
        merged.groupby("group")
        .agg(
            mean_response=("adjusted_response", "mean"),
            std_response=("adjusted_response", "std"),
            mean_covariate=("score", "mean"),
            n_trials=("trial", "count"),
        )
        .reset_index()
    )
    stx.io.save(stats, "neural.csv")
    logger.info(f"Neural stats for {len(stats)} groups")
    return 0


if __name__ == "__main__":
    main()

# EOF
