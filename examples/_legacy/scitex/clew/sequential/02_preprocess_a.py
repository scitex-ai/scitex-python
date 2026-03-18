#!/usr/bin/env python3
# Timestamp: "2026-02-01 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex-python/examples/scitex/verify/02_preprocess_a.py

"""Preprocess data A with config."""

from pathlib import Path

import scitex as stx

SCRIPT_DIR = Path(__file__).parent
OUTPUT_DIR = SCRIPT_DIR / "01_source_a_out"


@stx.session
def main(
    input_file: str = None,
    config_file: str = None,
    CONFIG=stx.session.INJECTED,
    logger=stx.session.INJECTED,
):
    """Preprocess data A with config."""
    input_file = input_file or str(OUTPUT_DIR / "source_A.csv")
    config_file = config_file or str(OUTPUT_DIR / "config_A.json")
    logger.info("Preprocessing source A")

    data = stx.io.load(input_file)
    config = stx.io.load(config_file)

    # Apply threshold from config
    data_clean = data[
        data["value"] > data["value"].quantile(config["threshold"])
    ].copy()
    data_clean["source"] = "A"

    stx.io.save(data_clean, "clean_A.csv")
    logger.info(f"Preprocessed {len(data_clean)} rows from source A")
    return 0


if __name__ == "__main__":
    main()


# EOF
