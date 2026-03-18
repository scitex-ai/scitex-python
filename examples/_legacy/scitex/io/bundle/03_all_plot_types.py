#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-12-21 03:12:00 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex-code/examples/scitex/io/bundle/03_all_plot_types.py

"""
Example 03: FTS Bundle Creation for All Plot Types

Demonstrates FTS bundle creation using all 61 plotters from scitex.dev.plt.
For each plotter: create figure, save as FTS, validate encoding-CSV linkage.
"""

import io
import json

import pandas as pd

import scitex as stx
import scitex.io as sio
from scitex import INJECTED
from scitex.dev.plt import PLOTTERS, PLOTTERS_MPL, PLOTTERS_SNS, PLOTTERS_STX
from scitex.io.bundle import FTS
from scitex.io.bundle._mpl_helpers import validate_encoding_csv_link


def validate_bundle(bundle):
    """Validate bundle's encoding-CSV link."""
    if not bundle.storage.exists("payload/data.csv"):
        return None, None  # No CSV data

    csv_bytes = bundle.storage.read("payload/data.csv")
    csv_df = pd.read_csv(io.BytesIO(csv_bytes))
    errors = validate_encoding_csv_link(bundle._encoding, csv_df)

    n_traces = len(bundle._encoding.traces) if bundle._encoding else 0
    n_cols = len(csv_df.columns)

    return errors, (n_traces, n_cols)


def process_plotter(plt, rng, out_dir, name, plotter, current, total, logger, results):
    """Process a single plotter."""
    try:
        fig, ax = plotter(plt, rng)
        bundle_path = out_dir / f"{name}.zip"
        sio.save(fig, bundle_path)
        plt.close(fig)

        bundle = FTS(bundle_path)
        errors, stats = validate_bundle(bundle)

        if errors is None:
            results["no_csv"].append(name)
            logger.info(f"[{current}/{total}] {name}: OK (no CSV)")
        elif errors:
            results["failed"].append((name, errors))
            logger.warning(f"[{current}/{total}] {name}: ERRORS - {errors}")
        else:
            results["success"].append(name)
            logger.info(f"[{current}/{total}] {name}: OK ({stats[0]} traces, {stats[1]} cols)")

    except Exception as e:
        results["failed"].append((name, str(e)))
        logger.error(f"[{current}/{total}] {name}: FAILED - {e}")
        try:
            plt.close("all")
        except Exception:
            pass


def print_summary(logger, results, total):
    """Print summary report."""
    logger.info(f"\n{'='*60}")
    logger.info("SUMMARY REPORT")
    logger.info(f"{'='*60}")
    logger.info(f"Total: {total}")
    logger.info(f"Success (with CSV): {len(results['success'])}")
    logger.info(f"Success (no CSV): {len(results['no_csv'])}")
    logger.info(f"Failed: {len(results['failed'])}")

    if results["failed"]:
        logger.warning("\nFailed plotters:")
        for name, error in results["failed"]:
            logger.warning(f"  - {name}: {error}")


def save_report(out_dir, results, total):
    """Save results to JSON file."""
    report = {
        "total": total,
        "success_with_csv": results["success"],
        "success_no_csv": results["no_csv"],
        "failed": [(n, str(e)) for n, e in results["failed"]],
    }
    report_path = out_dir / "test_report.json"
    with open(report_path, "w") as f:
        json.dump(report, f, indent=2)
    return report_path


@stx.session(verbose=False, agg=True)
def main(plt=INJECTED, CONFIG=INJECTED, logger=INJECTED, rngg=INJECTED):
    """Test FTS bundle creation for all plot types."""
    logger.info("Example 03: FTS Bundle Creation for All Plot Types")

    out_dir = CONFIG["SDIR_OUT"]
    rng = rng("fts_test")
    results = {"success": [], "failed": [], "no_csv": []}

    all_plotters = [
        ("stx", PLOTTERS_STX),
        ("sns", PLOTTERS_SNS),
        ("mpl", PLOTTERS_MPL),
    ]

    total = len(PLOTTERS)
    current = 0

    for api_name, plotters in all_plotters:
        logger.info(f"\n{'='*60}")
        logger.info(f"Testing {api_name.upper()} API ({len(plotters)} plotters)")
        logger.info(f"{'='*60}")

        for name, plotter in plotters.items():
            current += 1
            process_plotter(plt, rng, out_dir, name, plotter, current, total, logger, results)

    print_summary(logger, results, total)
    report_path = save_report(out_dir, results, total)
    logger.info(f"\nReport saved to: {report_path}")

    if not results["failed"]:
        logger.success(f"All {total} plotters passed!")
    else:
        logger.warning(f"{len(results['failed'])}/{total} plotters failed")

    logger.success("Example 03 completed!")


if __name__ == "__main__":
    main()

# EOF
