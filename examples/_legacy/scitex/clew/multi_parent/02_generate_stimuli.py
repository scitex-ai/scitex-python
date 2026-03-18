#!/usr/bin/env python3
# Timestamp: "2026-03-04 (ywatanabe)"
# File: examples/scitex/clew/multi_parent/02_generate_stimuli.py

"""Generate stimulus parameters."""

import pandas as pd

import scitex as stx


@stx.session
def main(
    n_stimuli: int = 40,
    CONFIG=stx.session.INJECTED,
    logger=stx.session.INJECTED,
    rngg=stx.session.INJECTED,
):
    """Generate stimulus parameters."""
    logger.info("Generating stimuli")
    rng = rngg("stimuli")

    data = pd.DataFrame(
        {
            "stimulus_id": [f"stim_{i:03d}" for i in range(n_stimuli)],
            "frequency_hz": rng.uniform(1.0, 100.0, n_stimuli).round(1),
            "duration_ms": rng.choice([100, 200, 500], n_stimuli),
            "modality": rng.choice(["visual", "auditory"], n_stimuli),
        }
    )
    stx.io.save(data, "stimuli.csv")
    logger.info(f"Generated {n_stimuli} stimuli")
    return 0


if __name__ == "__main__":
    main()

# EOF
