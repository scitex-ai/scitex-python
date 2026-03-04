#!/usr/bin/env python3
# Timestamp: "2026-03-04 (ywatanabe)"
# File: examples/scitex/clew/multi_parent/05_analyze_behavior.py

"""Analyze behavioral data from experiment."""

from pathlib import Path

import scitex as stx

SCRIPT_DIR = Path(__file__).parent


@stx.session
def main(
    input_file: str = None,
    CONFIG=stx.session.INJECTED,
    logger=stx.session.INJECTED,
):
    """Analyze behavioral data (reaction time, accuracy)."""
    input_file = input_file or str(
        SCRIPT_DIR / "03_run_experiment_out" / "raw_data.csv"
    )
    logger.info("Analyzing behavior")

    raw = stx.io.load(input_file)

    stats = (
        raw.groupby("group")
        .agg(
            mean_rt=("reaction_time_ms", "mean"),
            std_rt=("reaction_time_ms", "std"),
            accuracy=("accuracy", "mean"),
            n_trials=("trial", "count"),
        )
        .reset_index()
    )
    stx.io.save(stats, "behavior.csv")
    logger.info(f"Behavioral stats for {len(stats)} groups")
    return 0


if __name__ == "__main__":
    main()

# EOF
