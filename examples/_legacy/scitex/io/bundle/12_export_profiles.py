#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-12-21 03:12:00 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex-code/examples/scitex/io/bundle/13_export_profiles.py

"""
Example 13: Journal-Specific Theme Profiles

Demonstrates:
- Creating theme presets for different journals
- Same data with different visual styles
- Theme-based customization
"""

import shutil

import numpy as np

import scitex as stx
import scitex.io as sio
from scitex import INJECTED
from scitex.io.bundle import FTS

# Journal theme profiles
PROFILES = {
    "nature": {
        "name": "Nature",
        "mode": "light",
        "fonts": {"family": "Arial", "title_size": 10, "label_size": 8},
        "colors": {"primary": "#1f77b4", "secondary": "#ff7f0e"},
    },
    "cell": {
        "name": "Cell",
        "mode": "light",
        "fonts": {"family": "Helvetica", "title_size": 11, "label_size": 9},
        "colors": {"primary": "#2ca02c", "secondary": "#d62728"},
    },
    "ieee": {
        "name": "IEEE",
        "mode": "light",
        "fonts": {"family": "Times New Roman", "title_size": 10, "label_size": 8},
        "colors": {"primary": "#000000", "secondary": "#666666"},
    },
}


def cleanup_existing(out_dir, profile_ids):
    """Remove existing bundles."""
    for profile_id in profile_ids:
        path = out_dir / f"journal_{profile_id}.zip"
        if path.exists():
            shutil.rmtree(path) if path.is_dir() else path.unlink()


def generate_sample_data():
    """Generate sample signal data."""
    np.random.seed(42)
    x = np.linspace(0, 10, 100)
    y = np.sin(x) + np.random.normal(0, 0.1, 100)
    return x, y


def create_journal_bundle(plt, out_dir, profile_id, profile, x, y, logger):
    """Create bundle with journal-specific theme."""
    logger.info(f"\n--- Creating {profile['name']} styled bundle ---")

    fig, ax = plt.subplots(figsize=(3.5, 2.5))
    ax.plot(x, y, linewidth=1.5, color=profile["colors"]["primary"])
    ax.fill_between(x, y - 0.2, y + 0.2, alpha=0.3, color=profile["colors"]["primary"])
    ax.set_xlabel("Time (s)")
    ax.set_ylabel("Amplitude (mV)")
    ax.set_title(f"{profile['name']} Style")

    bundle_path = out_dir / f"journal_{profile_id}.zip"
    sio.save(fig, bundle_path)
    plt.close(fig)

    bundle = FTS(bundle_path)
    bundle.theme = {
        "mode": profile["mode"],
        "fonts": profile["fonts"],
        "colors": profile["colors"],
        "figure_title": {
            "text": f"Neural Response ({profile['name']} Format)",
            "prefix": "Figure",
            "number": 1,
        },
    }
    bundle.save()

    logger.info(f"  Created: {bundle_path.name}")
    logger.info(f"  Font: {profile['fonts']['family']}")
    logger.info(f"  Colors: {profile['colors']}")


def print_comparison_report(logger):
    """Print journal profile comparison."""
    logger.info("\n" + "=" * 60)
    logger.info("JOURNAL PROFILE COMPARISON")
    logger.info("=" * 60)

    logger.info(
        f"\n{'Journal':<10} {'Font':<20} {'Title Size':<12} {'Primary Color':<14}"
    )
    logger.info("-" * 56)

    for profile_id, profile in PROFILES.items():
        logger.info(
            f"{profile['name']:<10} {profile['fonts']['family']:<20} "
            f"{profile['fonts']['title_size']:<12} {profile['colors']['primary']:<14}"
        )


def verify_bundles(out_dir, logger):
    """Verify all bundles created."""
    logger.info("\n" + "-" * 40)
    logger.info("Created bundles:")
    for profile_id in PROFILES:
        bundle_path = out_dir / f"journal_{profile_id}.zip"
        bundle = FTS(bundle_path)
        logger.info(f"  {bundle_path.name}: mode={bundle.theme.mode}")


def print_summary(logger):
    """Print key takeaways."""
    logger.info("\n" + "=" * 60)
    logger.info("Key takeaway:")
    logger.info("  - Same data, different visual styles")
    logger.info("  - Theme defines journal-specific formatting")
    logger.info("  - Easy to switch between journal requirements")
    logger.info("=" * 60)


@stx.session(verbose=False, agg=True)
def main(plt=INJECTED, CONFIG=INJECTED, logger=INJECTED):
    """Demonstrate journal-specific theme profiles."""
    logger.info("Example 13: Journal Theme Profiles")

    out_dir = CONFIG["SDIR_OUT"]

    cleanup_existing(out_dir, PROFILES.keys())

    x, y = generate_sample_data()

    for profile_id, profile in PROFILES.items():
        create_journal_bundle(plt, out_dir, profile_id, profile, x, y, logger)

    print_comparison_report(logger)
    verify_bundles(out_dir, logger)
    print_summary(logger)

    logger.success("Example 13 completed!")


if __name__ == "__main__":
    main()

# EOF
