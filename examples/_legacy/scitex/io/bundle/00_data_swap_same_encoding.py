#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-12-21 03:10:00 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex-code/examples/scitex/io/bundle/00_data_swap_same_encoding.py

"""
Example: Data and Encoding Separation

Demonstrates:
- Encoding defines HOW to visualize (column mappings)
- Data contains WHAT to visualize (actual values)
- Same encoding can be used with different datasets
"""

import hashlib
import shutil

import numpy as np
import pandas as pd

import scitex as stx
import scitex.io as sio
from scitex import INJECTED
from scitex.io.bundle import FTS


def encoding_hash(bundle):
    """Compute MD5 hash of bundle's encoding.json."""
    try:
        enc_bytes = bundle.storage.read("canonical/encoding.json")
        return hashlib.md5(enc_bytes).hexdigest()[:12]
    except Exception:
        return None


def cleanup_existing(out_dir, names):
    """Remove existing bundles."""
    for name in names:
        path = out_dir / name
        if path.exists():
            shutil.rmtree(path) if path.is_dir() else path.unlink()


def create_encoding():
    """Create standard encoding for x/y scatter plot."""
    return {
        "traces": [
            {
                "trace_id": "main",
                "x": {"column": "x", "type": "quantitative"},
                "y": {"column": "y", "type": "quantitative"},
            }
        ],
        "axes": {
            "x": {"title": "X Axis", "type": "quantitative"},
            "y": {"title": "Y Axis", "type": "quantitative"},
        },
    }


def create_dataset(amplitude=1.0, noise=0.1, label="dataset"):
    """Generate synthetic signal data."""
    x = np.linspace(0, 10, 50)
    y = amplitude * np.sin(x) + np.random.normal(0, noise, 50)
    df = pd.DataFrame({"x": x, "y": y, "label": label})
    return x, y, df


def create_bundle(plt, bundle_path, x, y, df, title, color="C0"):
    """Create plot and save as FTS bundle with encoding."""
    fig, ax = plt.subplots(figsize=(4, 3))
    ax.plot(x, y, "o-", markersize=3, color=color)
    ax.set_xlabel("x")
    ax.set_ylabel("y")
    ax.set_title(title)

    sio.save(fig, bundle_path, data=df)
    plt.close(fig)

    bundle = FTS(bundle_path)
    bundle.encoding = create_encoding()
    bundle.save()

    return encoding_hash(bundle)


def print_report(logger, hash1, hash2, y1, y2):
    """Print comparison report."""
    logger.info("\n" + "=" * 60)
    logger.info("COMPARISON REPORT")
    logger.info("=" * 60)

    enc_status = "IDENTICAL" if hash1 == hash2 else "DIFFERENT"
    logger.info(f"\nEncoding comparison: {enc_status}")
    logger.info(f"  Bundle 1: {hash1}")
    logger.info(f"  Bundle 2: {hash2}")

    logger.info("\nData comparison:")
    logger.info(f"  Dataset 1 y-range: [{y1.min():.2f}, {y1.max():.2f}]")
    logger.info(f"  Dataset 2 y-range: [{y2.min():.2f}, {y2.max():.2f}]")
    logger.info(f"  Range increased: {(y2.max() - y2.min()) > (y1.max() - y1.min())}")

    logger.info("\n" + "=" * 60)
    logger.info("Key takeaways:")
    logger.info("  - encoding.json defines HOW to plot (x→x, y→y mappings)")
    logger.info("  - data.csv contains WHAT to plot (actual values)")
    logger.info("  - Same encoding + different data = different visualization")
    logger.info("  - Enables reproducible, swappable data pipelines")
    logger.info("=" * 60)


@stx.session(verbose=False, agg=True)
def main(plt=INJECTED, CONFIG=INJECTED, logger=INJECTED):
    """Demonstrate data/encoding separation."""
    logger.info("Example: Data and Encoding Separation")

    out_dir = CONFIG["SDIR_OUT"]
    cleanup_existing(out_dir, ["data_encoding_demo.zip", "data_encoding_demo_2.zip"])

    np.random.seed(42)

    # Dataset 1: Low amplitude
    logger.info("\n" + "=" * 60)
    logger.info("DATASET 1: Low amplitude signal")
    logger.info("=" * 60)

    x1, y1, df1 = create_dataset(amplitude=1.0, noise=0.1, label="dataset_1")
    logger.info(f"  y range: [{y1.min():.2f}, {y1.max():.2f}]")

    hash1 = create_bundle(
        plt, out_dir / "data_encoding_demo.zip", x1, y1, df1, "Dataset 1"
    )
    logger.info(f"  encoding.json hash: {hash1}")

    # Dataset 2: High amplitude (3x)
    logger.info("\n" + "=" * 60)
    logger.info("DATASET 2: High amplitude signal (same columns)")
    logger.info("=" * 60)

    x2, y2, df2 = create_dataset(amplitude=3.0, noise=0.3, label="dataset_2")
    logger.info(f"  y range: [{y2.min():.2f}, {y2.max():.2f}]")

    hash2 = create_bundle(
        plt, out_dir / "data_encoding_demo_2.zip", x2, y2, df2, "Dataset 2", "red"
    )
    logger.info(f"  encoding.json hash: {hash2}")

    # Report
    print_report(logger, hash1, hash2, y1, y2)

    logger.success("Example completed!")


if __name__ == "__main__":
    main()

# EOF
