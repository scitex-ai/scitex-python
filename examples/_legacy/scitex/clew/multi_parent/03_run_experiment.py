#!/usr/bin/env python3
# Timestamp: "2026-03-04 (ywatanabe)"
# File: examples/scitex/clew/multi_parent/03_run_experiment.py

"""Run experiment combining subjects, stimuli, and covariates (3-parent merge)."""

from pathlib import Path

import pandas as pd

import scitex as stx

SCRIPT_DIR = Path(__file__).parent


@stx.session
def main(
    subjects_file: str = None,
    stimuli_file: str = None,
    covariates_file: str = None,
    CONFIG=stx.session.INJECTED,
    logger=stx.session.INJECTED,
    rngg=stx.session.INJECTED,
):
    """Run experiment (3-parent: subjects + stimuli + covariates)."""
    subjects_file = subjects_file or str(
        SCRIPT_DIR / "01_generate_subjects_out" / "subjects.csv"
    )
    stimuli_file = stimuli_file or str(
        SCRIPT_DIR / "02_generate_stimuli_out" / "stimuli.csv"
    )
    covariates_file = covariates_file or str(
        SCRIPT_DIR / "04_load_covariates_out" / "covariates.csv"
    )

    logger.info("Running experiment")
    rng = rngg("experiment")

    subjects = stx.io.load(subjects_file)
    stimuli = stx.io.load(stimuli_file)
    covariates = stx.io.load(covariates_file)

    # Cross subjects x stimuli subset, attach covariates
    n_trials = len(subjects) * 5
    rows = []
    for i in range(n_trials):
        subj = subjects.iloc[i % len(subjects)]
        stim = stimuli.iloc[rng.integers(0, len(stimuli))]
        cov = covariates.iloc[i % len(covariates)]
        rows.append(
            {
                "trial": i,
                "subject_id": subj["subject_id"],
                "group": subj["group"],
                "stimulus_id": stim["stimulus_id"],
                "modality": stim["modality"],
                "covariate_score": cov["score"],
                "reaction_time_ms": rng.normal(400, 80),
                "accuracy": rng.choice([0, 1], p=[0.2, 0.8]),
                "neural_response": rng.normal(0.5, 0.3),
            }
        )

    raw_data = pd.DataFrame(rows)
    stx.io.save(raw_data, "raw_data.csv")
    logger.info(f"Generated {n_trials} trials from 3 sources")
    return 0


if __name__ == "__main__":
    main()

# EOF
