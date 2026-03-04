#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2026-02-01 08:40:03 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex-python/examples/scitex/verify/05_source_c.py


"""Generate source data C."""

import pandas as pd

import scitex as stx


@stx.session
def main(
    n_samples: int = 250,
    CONFIG=stx.session.INJECTED,
    logger=stx.session.INJECTED,
    rngg=stx.session.INJECTED,
):
    """Generate source data C."""
    logger.info("Generating source C")
    rng = rngg("source_c")

    data = pd.DataFrame(
        {
            "id": range(n_samples),
            "value": rng.standard_normal(n_samples) * 8 + 75,
            "category": rng.choice(["X", "Z"], n_samples),
        }
    )
    stx.io.save(data, "source_C.csv")

    logger.info(f"Generated {n_samples} samples for source C")
    return 0


if __name__ == "__main__":
    main()

# EOF
