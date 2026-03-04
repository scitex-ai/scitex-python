#!/usr/bin/env python3
# Timestamp: "2026-02-01 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex-python/examples/scitex/verify/07_merge.py

"""Merge all three branches."""

from pathlib import Path

import pandas as pd

import scitex as stx

SCRIPT_DIR = Path(__file__).parent


@stx.session
def main(
    input_a: str = None,
    input_b: str = None,
    input_c: str = None,
    CONFIG=stx.session.INJECTED,
    logger=stx.session.INJECTED,
):
    """Merge all three branches."""
    input_a = input_a or str(SCRIPT_DIR / "02_preprocess_a_out" / "clean_A.csv")
    input_b = input_b or str(SCRIPT_DIR / "04_preprocess_b_out" / "clean_B.csv")
    input_c = input_c or str(SCRIPT_DIR / "06_preprocess_c_out" / "clean_C.csv")
    logger.info("Merging all branches")

    data_a = stx.io.load(input_a)
    data_b = stx.io.load(input_b)
    data_c = stx.io.load(input_c)

    merged = pd.concat([data_a, data_b, data_c], ignore_index=True)
    merged["combined_score"] = merged["value"] * 1.1

    stx.io.save(merged, "final.csv")
    logger.info(f"Merged {len(merged)} total rows from 3 sources")
    return 0


if __name__ == "__main__":
    main()


# EOF
