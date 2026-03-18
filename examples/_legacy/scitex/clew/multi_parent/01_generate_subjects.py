#!/usr/bin/env python3
# Timestamp: "2026-03-04 (ywatanabe)"
# File: examples/scitex/clew/multi_parent/01_generate_subjects.py

"""Generate subject demographics data."""

import pandas as pd

import scitex as stx


@stx.session
def main(
    n_subjects: int = 30,
    CONFIG=stx.session.INJECTED,
    logger=stx.session.INJECTED,
    rngg=stx.session.INJECTED,
):
    """Generate subject demographics data."""
    logger.info("Generating subject demographics")
    rng = rngg("subjects")

    data = pd.DataFrame(
        {
            "subject_id": [f"S{i:03d}" for i in range(n_subjects)],
            "age": rng.integers(20, 65, n_subjects),
            "group": rng.choice(["control", "treatment"], n_subjects),
        }
    )
    stx.io.save(data, "subjects.csv")
    logger.info(f"Generated {n_subjects} subjects")
    return 0


if __name__ == "__main__":
    main()

# EOF
