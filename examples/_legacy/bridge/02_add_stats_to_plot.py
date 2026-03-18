#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: 2025-12-09
# File: ./examples/bridge/02_add_stats_to_plot.py
"""
Example: Add statistical annotations to plots

Demonstrates adding StatResult annotations to matplotlib plots:
1. Create a plot
2. Create StatResult objects from statistical tests
3. Add them as structured annotations
4. Extract and inspect the annotations

This enables:
- Structured statistical notation (not just text)
- Round-trip extraction of stats from figures
- GUI editing of stat annotations

Usage:
    python 02_add_stats_to_plot.py
"""

from pathlib import Path

import numpy as np
import scitex as stx
from scipy import stats
from scitex.bridge import (
    add_stat_to_axes,
    extract_stats_from_axes,
)
from scitex.schema import create_stat_result


@stx.session
def main(
    CONFIG=stx.INJECTED,
    plt=stx.INJECTED,
    logger=stx.INJECTED,
):
    """Add statistical annotations to plots."""
    out = Path(CONFIG.SDIR_OUT)

    # 1. Create sample data
    group_a = np.random.normal(100, 15, 30)
    group_b = np.random.normal(110, 15, 30)

    # 2. Perform statistical test
    t_stat, p_value = stats.ttest_ind(group_a, group_b)

    logger.info("=" * 60)
    logger.info("Statistical Test Results")
    logger.info("=" * 60)
    logger.info(f"t-statistic: {t_stat:.3f}")
    logger.info(f"p-value: {p_value:.4f}")

    # Define group labels (consistent with plot labels)
    GROUP_LABELS = ["Group A", "Group B"]

    # 3. Create StatResult with sample info for consistent naming
    stat_result = create_stat_result(
        test_type="t-test",
        statistic_name="t",
        statistic_value=t_stat,
        p_value=p_value,
        samples={
            GROUP_LABELS[0]: {"n": len(group_a), "mean": float(np.mean(group_a)), "std": float(np.std(group_a))},
            GROUP_LABELS[1]: {"n": len(group_b), "mean": float(np.mean(group_b)), "std": float(np.std(group_b))},
        },
    )

    logger.info(f"Stars: {stat_result.stars}")
    logger.info(f"Format (asterisk): {stat_result.format_text('asterisk')}")
    logger.info(f"Format (compact): {stat_result.format_text('compact')}")
    logger.info(f"Format (publication): {stat_result.format_text('publication')}")

    # 4. Create figure and add annotation
    fig, ax = plt.subplots(figsize=(8, 6))

    # Box plot (use same GROUP_LABELS for consistent naming)
    ax.boxplot([group_a, group_b], labels=GROUP_LABELS)
    ax.set_xyt(x="", y="Value", t="Comparison between Groups")

    # Add stat annotation using the bridge
    # Position inside the plot area (axes coordinates: 0-1)
    add_stat_to_axes(
        ax,
        stat_result,
        x=0.5,
        y=0.92,  # Position inside axes area
        format_style="asterisk",
    )

    # Also add publication format at different location
    add_stat_to_axes(
        ax,
        stat_result,
        x=0.5,
        y=0.82,
        format_style="publication",
    )

    # 5. Extract stats back from the plot
    logger.info("-" * 60)
    logger.info("Extracted Statistics from Plot")
    logger.info("-" * 60)

    extracted = extract_stats_from_axes(ax)
    for i, s in enumerate(extracted):
        logger.info(f"Stat {i + 1}:")
        logger.info(f"  Test type: {s.test_type}")
        logger.info(f"  Statistic: {s.statistic['name']} = {s.statistic['value']:.3f}")
        logger.info(f"  P-value: {s.p_value:.4f}")
        logger.info(f"  Stars: {s.stars}")

    # 6. Note: Stats are auto-saved when fig is saved (as {basename}_stats.csv)
    # For additional details like sample sizes and descriptive stats,
    # manual saving can include more context:
    import pandas as pd

    # Build detailed stats with consistent group naming
    detailed_row = {
        "test_type": stat_result.test_type,
        "statistic_name": stat_result.statistic["name"],
        "statistic_value": stat_result.statistic["value"],
        "p_value": stat_result.p_value,
        "stars": stat_result.stars,
        "effect_size": stat_result.effect_size.get("value") if stat_result.effect_size else None,
    }
    # Add sample info from StatResult (consistent with GROUP_LABELS)
    if stat_result.samples:
        for group_name, group_info in stat_result.samples.items():
            detailed_row[f"n_{group_name}"] = group_info.get("n")
            detailed_row[f"mean_{group_name}"] = group_info.get("mean")
            detailed_row[f"std_{group_name}"] = group_info.get("std")

    detailed_stats_df = pd.DataFrame([detailed_row])

    detailed_stats_path = out / "add_stats_to_plot_detailed.csv"
    stx.io.save(detailed_stats_df, detailed_stats_path)
    logger.info(f"Detailed stats saved to: {detailed_stats_path}")

    # 7. Save figure
    png_path = out / "add_stats_to_plot.png"
    stx.io.save(fig, png_path)
    logger.info(f"Figure saved to: {png_path}")

    fig.close()
    logger.info("Done!")


if __name__ == "__main__":
    main()

# EOF
