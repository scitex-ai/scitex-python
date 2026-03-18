#!/usr/bin/env python3
# Timestamp: "2026-03-04 (ywatanabe)"
# File: examples/scitex/clew/multi_parent/08_make_figures.py

"""Generate publication figures from combined results."""

from pathlib import Path

import scitex as stx

SCRIPT_DIR = Path(__file__).parent


@stx.session
def main(
    input_file: str = None,
    CONFIG=stx.session.INJECTED,
    logger=stx.session.INJECTED,
    plt=stx.session.INJECTED,
):
    """Generate figures from combined results."""
    input_file = input_file or str(SCRIPT_DIR / "07_merge_results_out" / "combined.csv")
    logger.info("Making figures")

    combined = stx.io.load(input_file)

    # Figure 1: Behavioral comparison
    fig1, ax1 = plt.subplots()
    groups = combined["group"].tolist()
    ax1.bar(groups, combined["accuracy"].tolist())
    ax1.set_xyt("Group", "Accuracy", "Behavioral Performance")
    stx.io.save(fig1, "figure1.png")

    # Figure 2: Neural response comparison
    fig2, ax2 = plt.subplots()
    ax2.bar(groups, combined["mean_response"].tolist())
    ax2.set_xyt("Group", "Neural Response", "Adjusted Neural Activity")
    stx.io.save(fig2, "figure2.png")

    logger.info("Generated 2 figures")
    return 0


if __name__ == "__main__":
    main()

# EOF
