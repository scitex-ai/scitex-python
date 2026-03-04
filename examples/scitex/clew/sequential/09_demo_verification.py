#!/usr/bin/env python3
# Timestamp: "2026-02-01 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex-python/examples/scitex/verify/09_demo_verification.py

"""Demo verification states: rerun, break chain, and visualize DAG."""

from pathlib import Path

import pandas as pd

import scitex as stx

SCRIPT_DIR = Path(__file__).parent


def _verify_by_rerun():
    """Verify source_A by re-running to demonstrate ✓✓ badge."""
    from scitex.clew import verify_by_rerun

    target = str(SCRIPT_DIR / "01_source_a_out" / "source_A.csv")
    result = verify_by_rerun(target)
    print(f"  {'✓✓' if result.is_verified else '✗'} source_A.csv")


def _break_chain():
    """Modify clean_C.csv to simulate verification failure."""
    clean_c = SCRIPT_DIR / "06_preprocess_c_out" / "clean_C.csv"
    if clean_c.exists():
        data = pd.read_csv(clean_c)
        data["value"] = data["value"] * 1.001
        data.to_csv(clean_c, index=False)
        print(f"  Modified {clean_c.name} to simulate failure")
    else:
        print(f"  Warning: {clean_c} not found")


def _visualize():
    """Generate DAG visualization in multiple formats."""
    from scitex.clew import render_dag

    target = str(SCRIPT_DIR / "08_analyze_out" / "report.json")
    title = "Verification DAG (Multi-Script Pipeline)"

    for fmt in ["html", "svg", "png"]:
        output_path = SCRIPT_DIR / "09_demo_verification_out" / f"dag.{fmt}"
        output_path.parent.mkdir(parents=True, exist_ok=True)
        try:
            render_dag(
                str(output_path), target_file=target, title=title, show_hashes=True
            )
            print(f"  Generated: {output_path}")
        except Exception as e:
            print(f"  Skipped {fmt}: {e}")


@stx.session
def main(
    action: str = "all",
    CONFIG=stx.session.INJECTED,
    logger=stx.session.INJECTED,
):
    """Demo verification states.

    Actions:
        rerun     - Record rerun verification for some sessions
        break     - Modify clean_C.csv to cause verification failure
        visualize - Generate DAG visualization
        all       - Run all actions in sequence
    """
    if action in ("rerun", "all"):
        logger.info("Recording rerun verification...")
        _verify_by_rerun()

    if action in ("break", "all"):
        logger.info("Breaking chain by modifying clean_C.csv...")
        _break_chain()

    if action in ("visualize", "all"):
        logger.info("Generating DAG visualization...")
        _visualize()

    return 0


if __name__ == "__main__":
    main()


# EOF
