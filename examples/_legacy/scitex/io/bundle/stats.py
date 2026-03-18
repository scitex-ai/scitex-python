#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-12-20 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex-code/examples/scitex/io/bundle/statsz.py

"""
Demonstrates FTS stats bundle creation and loading.

FTS bundles (replacing legacy .stats) contain:
- stats/stats.json: Statistical results (comparisons, p-values, effect sizes)
- node.json: Metadata (n, seed, bootstrap iterations, etc.)

Purpose:
- Store expensive test results (bootstrap, permutation)
- Reuse stats across multiple figure bundles
- Ensure full reproducibility
"""

# Imports
import scitex as stx
import scitex.stats as sstats


# Functions and Classes
def create_basic_comparisons():
    """Create basic statistical comparisons."""
    return [
        {
            "name": "Control vs Treatment A",
            "method": "t-test",
            "p_value": 0.003,
            "effect_size": 1.21,
            "ci95": [0.5, 1.8],
            "formatted": "**",
        },
    ]


def create_longitudinal_comparisons():
    """Create longitudinal study comparisons."""
    return [
        {
            "name": "Baseline vs Week 1",
            "method": "paired t-test",
            "p_value": 0.12,
            "effect_size": 0.35,
            "ci95": [-0.1, 0.8],
            "formatted": "ns",
        },
        {
            "name": "Baseline vs Week 2",
            "method": "paired t-test",
            "p_value": 0.03,
            "effect_size": 0.72,
            "ci95": [0.2, 1.2],
            "formatted": "*",
        },
        {
            "name": "Baseline vs Week 4",
            "method": "paired t-test",
            "p_value": 0.001,
            "effect_size": 1.45,
            "ci95": [0.8, 2.1],
            "formatted": "***",
        },
        {
            "name": "Week 1 vs Week 4",
            "method": "paired t-test",
            "p_value": 0.008,
            "effect_size": 0.98,
            "ci95": [0.4, 1.6],
            "formatted": "**",
        },
    ]


def create_bootstrap_results():
    """Create bootstrap analysis results."""
    comparisons = [
        {
            "name": "Group A vs Group B",
            "method": "bootstrap",
            "p_value": 0.017,
            "effect_size": 0.89,
            "ci95": [0.42, 1.36],
            "ci99": [0.28, 1.50],
            "formatted": "*",
            "bootstrap_samples": 10000,
            "observed_diff": 2.34,
        },
    ]
    metadata = {
        "method": "percentile bootstrap",
        "n_bootstrap": 10000,
        "seed": 12345,
        "n_group_a": 35,
        "n_group_b": 38,
        "computation_time_sec": 12.5,
    }
    return comparisons, metadata


@stx.session
def main(
    CONFIG=stx.session.INJECTED,
    plt=stx.session.INJECTED,
    COLORS=stx.session.INJECTED,
    rngg=stx.session.INJECTED,
    logger=stx.session.INJECTED,
):
    """Demonstrates FTS stats bundle functionality."""
    logger.info("Starting FTS stats bundle demo")

    sdir = CONFIG["SDIR_RUN"]

    # 1. Create basic statistical comparison
    logger.info("Creating basic comparison bundle")
    comparisons = create_basic_comparisons()
    sstats.save_stats(comparisons, sdir / "basic.stx")

    # Load and verify
    loaded = sstats.load_stats(sdir / "basic.stx")
    logger.info(f"Loaded {len(loaded['comparisons'])} comparisons")
    logger.success("Basic bundle created and verified")

    # 2. Create multi-comparison analysis with metadata
    logger.info("Creating longitudinal study bundle")
    multi_comparisons = create_longitudinal_comparisons()
    metadata = {
        "experiment": "Longitudinal Treatment Study",
        "n_subjects": 24,
        "correction": "bonferroni",
        "alpha": 0.05,
        "seed": 42,
    }
    sstats.save_stats(multi_comparisons, sdir / "longitudinal.stx", metadata=metadata)

    # Load and verify
    loaded_multi = sstats.load_stats(sdir / "longitudinal.stx")
    logger.info(f"Loaded {len(loaded_multi['comparisons'])} comparisons with metadata")
    logger.success("Longitudinal bundle created")

    # 3. Bootstrap results
    logger.info("Creating bootstrap results bundle")
    bootstrap_comps, bootstrap_meta = create_bootstrap_results()
    sstats.save_stats(
        bootstrap_comps, sdir / "bootstrap_results.stx", metadata=bootstrap_meta
    )
    logger.success("Bootstrap bundle created")

    # 4. Save as ZIP archive
    logger.info("Creating ZIP archive")
    sstats.save_stats(comparisons, sdir / "results.zip", as_zip=True)
    logger.success("ZIP bundle created")

    # Summary table
    logger.info("Results summary:")
    for comp in loaded_multi["comparisons"]:
        logger.info(
            f"  {comp['name']}: p={comp['p_value']:.4f}, "
            f"d={comp['effect_size']:.2f}, {comp['formatted']}"
        )

    logger.success("Demo completed")
    return 0


if __name__ == "__main__":
    main()

# EOF
