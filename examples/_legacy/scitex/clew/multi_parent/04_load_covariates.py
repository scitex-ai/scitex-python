#!/usr/bin/env python3
# Timestamp: "2026-03-04 (ywatanabe)"
# File: examples/scitex/clew/multi_parent/04_load_covariates.py

"""Generate covariate data (e.g., clinical scores, demographics)."""

import pandas as pd

import scitex as stx


@stx.session
def main(
    n_entries: int = 30,
    CONFIG=stx.session.INJECTED,
    logger=stx.session.INJECTED,
    rngg=stx.session.INJECTED,
):
    """Generate covariate data."""
    logger.info("Generating covariates")
    rng = rngg("covariates")

    data = pd.DataFrame(
        {
            "subject_id": [f"S{i:03d}" for i in range(n_entries)],
            "score": rng.normal(50, 10, n_entries).round(1),
            "handedness": rng.choice(["L", "R"], n_entries, p=[0.1, 0.9]),
        }
    )
    stx.io.save(data, "covariates.csv")
    logger.info(f"Generated {n_entries} covariate entries")
    return 0


if __name__ == "__main__":
    main()

# EOF
