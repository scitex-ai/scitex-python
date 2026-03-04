#!/usr/bin/env python3
# Timestamp: "2026-02-01 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex-python/examples/scitex/verify/08_analyze.py

"""Analyze merged data and generate report."""

from pathlib import Path

import scitex as stx

SCRIPT_DIR = Path(__file__).parent


@stx.session
def main(
    input_file: str = None,
    CONFIG=stx.session.INJECTED,
    logger=stx.session.INJECTED,
):
    """Analyze merged data and generate report."""
    input_file = input_file or str(SCRIPT_DIR / "07_merge_out" / "final.csv")
    logger.info("Analyzing final merged data")

    data = stx.io.load(input_file)

    # Statistics by source
    stats = (
        data.groupby("source")
        .agg({"value": ["mean", "std", "count"], "combined_score": ["mean", "max"]})
        .round(2)
    )

    stx.io.save(stats.reset_index(), "stats_by_source.csv")

    # Final report
    report = {
        "total_records": len(data),
        "sources": list(data["source"].unique()),
        "categories": list(data["category"].unique()),
        "overall_mean": float(data["value"].mean()),
        "overall_std": float(data["value"].std()),
        "max_combined_score": float(data["combined_score"].max()),
    }
    stx.io.save(report, "report.json")

    logger.info("Analysis complete")
    return 0


if __name__ == "__main__":
    main()


# EOF
