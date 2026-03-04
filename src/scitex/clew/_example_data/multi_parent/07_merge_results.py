#!/usr/bin/env python3
# Timestamp: "2026-03-04 (ywatanabe)"
# File: examples/scitex/clew/multi_parent/07_merge_results.py

"""Merge behavioral and neural analysis results (2-parent merge)."""

from pathlib import Path

import scitex as stx

SCRIPT_DIR = Path(__file__).parent


@stx.session
def main(
    behavior_file: str = None,
    neural_file: str = None,
    CONFIG=stx.session.INJECTED,
    logger=stx.session.INJECTED,
):
    """Merge behavioral and neural results (2 parents)."""
    behavior_file = behavior_file or str(
        SCRIPT_DIR / "05_analyze_behavior_out" / "behavior.csv"
    )
    neural_file = neural_file or str(
        SCRIPT_DIR / "06_analyze_neural_out" / "neural.csv"
    )
    logger.info("Merging analysis results")

    behavior = stx.io.load(behavior_file)
    neural = stx.io.load(neural_file)

    combined = behavior.merge(neural, on="group", suffixes=("_beh", "_neu"))
    combined["composite_score"] = (
        combined["accuracy"] * 0.5 + combined["mean_response"] * 0.5
    )

    stx.io.save(combined, "combined.csv")
    logger.info(f"Merged results: {len(combined)} groups")
    return 0


if __name__ == "__main__":
    main()

# EOF
