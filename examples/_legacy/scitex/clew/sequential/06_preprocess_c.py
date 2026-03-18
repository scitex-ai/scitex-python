#!/usr/bin/env python3
# Timestamp: "2026-02-01 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex-python/examples/scitex/verify/06_preprocess_c.py

"""Preprocess data C."""

from pathlib import Path

import scitex as stx

SCRIPT_DIR = Path(__file__).parent
OUTPUT_DIR = SCRIPT_DIR / "05_source_c_out"


@stx.session
def main(
    input_file: str = None,
    CONFIG=stx.session.INJECTED,
    logger=stx.session.INJECTED,
):
    """Preprocess data C."""
    input_file = input_file or str(OUTPUT_DIR / "source_C.csv")
    logger.info("Preprocessing source C")

    data = stx.io.load(input_file)
    data_clean = data[data["value"] > 70].copy()
    data_clean["source"] = "C"

    stx.io.save(data_clean, "clean_C.csv")
    logger.info(f"Preprocessed {len(data_clean)} rows from source C")
    return 0


if __name__ == "__main__":
    main()


# EOF
