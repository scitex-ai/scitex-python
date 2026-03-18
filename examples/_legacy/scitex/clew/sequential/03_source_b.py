#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2026-02-01 08:39:47 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex-python/examples/scitex/verify/03_source_b.py


"""Generate source data B."""

import pandas as pd

import scitex as stx


@stx.session
def main(
    n_samples: int = 300,
    CONFIG=stx.session.INJECTED,
    logger=stx.session.INJECTED,
    rngg=stx.session.INJECTED,
):
    """Generate source data B."""
    logger.info("Generating source B")
    rng = rngg("source_b")

    data = pd.DataFrame(
        {
            "id": range(n_samples),
            "value": rng.standard_normal(n_samples) * 5 + 50,
            "category": rng.choice(["X", "Y", "Z"], n_samples),
        }
    )
    stx.io.save(data, "source_B.csv")

    logger.info(f"Generated {n_samples} samples for source B")
    return 0


if __name__ == "__main__":
    main()

# EOF
