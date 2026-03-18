#!/usr/bin/env python3
# Timestamp: "2026-02-01 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex-python/examples/scitex/verify/04_preprocess_b.py

"""Preprocess data B."""

from pathlib import Path

import scitex as stx

SCRIPT_DIR = Path(__file__).parent
OUTPUT_DIR = SCRIPT_DIR / "03_source_b_out"


@stx.session
def main(
    input_file: str = None,
    CONFIG=stx.session.INJECTED,
    logger=stx.session.INJECTED,
):
    """Preprocess data B."""
    input_file = input_file or str(OUTPUT_DIR / "source_B.csv")
    logger.info("Preprocessing source B")

    data = stx.io.load(input_file)
    data_clean = data[data["value"] > 45].copy()
    data_clean["source"] = "B"

    stx.io.save(data_clean, "clean_B.csv")
    logger.info(f"Preprocessed {len(data_clean)} rows from source B")
    return 0


if __name__ == "__main__":
    main()


# EOF
