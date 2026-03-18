#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-12-21 03:12:00 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex-code/examples/scitex/io/bundle/12_stats_annotation_binding.py

"""
Example 12: FTS Stats Integration

Demonstrates:
- Storing statistical results in FTS bundles
- Using scitex.stats with FTS
- Converting test results to Stats schema
"""

import shutil

import numpy as np
from scipy import stats as scipy_stats

import scitex as stx
import scitex.io as sio
import scitex.stats as sstats
from scitex import INJECTED
from scitex.io.bundle import FTS


def cleanup_existing(out_dir, name):
    """Remove existing bundle."""
    path = out_dir / name
    if path.exists():
        shutil.rmtree(path) if path.is_dir() else path.unlink()


def generate_sample_data():
    """Generate two-group sample data."""
    np.random.seed(42)
    return {
        "control": np.random.normal(5.0, 1.0, 30),
        "treatment": np.random.normal(7.0, 1.2, 30),
    }


def compute_statistics(data, logger):
    """Compute statistics for group comparison."""
    t_stat, p_value = scipy_stats.ttest_ind(data["control"], data["treatment"])
    effect_size = (np.mean(data["treatment"]) - np.mean(data["control"])) / np.std(
        data["control"]
    )

    logger.info(f"Statistical test: t={t_stat:.3f}, p={p_value:.6f}")
    logger.info(f"Effect size (Cohen's d): {effect_size:.3f}")
    logger.info(f"Significance: {sstats.p_to_stars(p_value)}")

    return {
        "t_stat": t_stat,
        "p_value": p_value,
        "effect_size": effect_size,
    }


def create_plot(plt, data, stats_result, out_dir):
    """Create bar plot with significance indicator."""
    fig, ax = plt.subplots(figsize=(4, 3))

    means = [np.mean(data["control"]), np.mean(data["treatment"])]
    stds = [np.std(data["control"]), np.std(data["treatment"])]
    x_pos = [0, 1]

    ax.bar(x_pos, means, yerr=stds, capsize=5, color=["#4A90D9", "#D94A4A"])
    ax.set_xticks(x_pos)
    ax.set_xticklabels(["Control", "Treatment"])
    ax.set_ylabel("Value")
    ax.set_title("Group Comparison")

    # Add significance indicator
    y_max = max(means) + max(stds) + 0.5
    ax.plot([0, 0, 1, 1], [y_max, y_max + 0.3, y_max + 0.3, y_max], "k-", lw=1.2)
    ax.text(
        0.5,
        y_max + 0.4,
        sstats.p_to_stars(stats_result["p_value"]),
        ha="center",
        fontsize=14,
    )

    bundle_path = out_dir / "stats_binding.zip"
    sio.save(fig, bundle_path)
    plt.close(fig)

    return bundle_path


def create_stats_result(stats):
    """Create stats result dict for FTS."""
    return {
        "name": "Control vs Treatment",
        "method": "independent_t_test",
        "statistic": float(stats["t_stat"]),
        "statistic_name": "t",
        "p_value": float(stats["p_value"]),
        "effect_size": float(stats["effect_size"]),
        "ci95": [stats["effect_size"] - 0.5, stats["effect_size"] + 0.5],
    }


def add_stats_to_bundle(bundle_path, stats_result, logger):
    """Load bundle and add stats."""
    bundle = FTS(bundle_path)

    if sstats.FTS_AVAILABLE:
        fts_stats = sstats.test_result_to_stats(stats_result)
        bundle.stats = fts_stats
        bundle.save()

        logger.info("\nStats added to bundle:")
        logger.info(f"  Analyses: {len(bundle.stats.analyses)}")
        if bundle.stats.analyses:
            a = bundle.stats.analyses[0]
            logger.info(f"  Method: {a.method.name}")
            logger.info(f"  p-value: {a.results.p_value}")
    else:
        logger.warning("FTS Stats schema not available")


def verify_stats(bundle_path, logger):
    """Reload and verify stats."""
    logger.info("\n" + "=" * 60)
    logger.info("STATS VERIFICATION")
    logger.info("=" * 60)

    reloaded = FTS(bundle_path)
    if reloaded.stats and reloaded.stats.analyses:
        for analysis in reloaded.stats.analyses:
            logger.info(f"\nAnalysis: {analysis.result_id[:12]}...")
            logger.info(f"  Method: {analysis.method.name}")
            logger.info(f"  Statistic: {analysis.results.statistic:.3f}")
            logger.info(f"  p-value: {analysis.results.p_value:.6f}")
            logger.info(f"  Significant: {analysis.results.significant}")
            if analysis.results.effect_size:
                logger.info(f"  Effect size: {analysis.results.effect_size.value:.3f}")


def print_summary(logger):
    """Print summary of stats integration."""
    logger.info("\n" + "=" * 60)
    logger.info("Key takeaway:")
    logger.info("  - FTS bundles can store statistical results")
    logger.info("  - Stats are linked to the figure data")
    logger.info("  - Enables reproducible statistical reporting")
    logger.info("=" * 60)


@stx.session(verbose=False, agg=True)
def main(plt=INJECTED, CONFIG=INJECTED, logger=INJECTED):
    """Demonstrate FTS stats integration."""
    logger.info("Example 12: FTS Stats Integration")

    out_dir = CONFIG["SDIR_OUT"]

    cleanup_existing(out_dir, "stats_binding.zip")

    data = generate_sample_data()
    stats = compute_statistics(data, logger)

    bundle_path = create_plot(plt, data, stats, out_dir)
    stats_result = create_stats_result(stats)
    add_stats_to_bundle(bundle_path, stats_result, logger)
    verify_stats(bundle_path, logger)
    print_summary(logger)

    logger.success("Example 12 completed!")


if __name__ == "__main__":
    main()

# EOF
