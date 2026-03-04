#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2026-02-01 08:38:41 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex-python/examples/scitex/verify/01_source_a.py


"""Generate source data A with config."""

import pandas as pd

import scitex as stx


@stx.session
def main(
    n_samples: int = 200,
    CONFIG=stx.session.INJECTED,
    logger=stx.session.INJECTED,
    rngg=stx.session.INJECTED,
):
    """Generate source data A with config."""
    logger.info("Generating source A")
    rng = rngg("source_a")

    data = pd.DataFrame(
        {
            "id": range(n_samples),
            "value": rng.standard_normal(n_samples) * 10 + 100,
            "category": rng.choice(["X", "Y"], n_samples),
        }
    )
    stx.io.save(data, "source_A.csv")

    config = {"threshold": 0.5, "method": "mean", "source": "A"}
    stx.io.save(config, "config_A.json")

    logger.info(f"Generated {n_samples} samples for source A")
    return 0


if __name__ == "__main__":
    main()

# EOF
