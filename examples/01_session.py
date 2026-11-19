#!/usr/bin/env python3
"""Example: @stx.session -- Reproducible Experiment Tracking

Every analysis parameter lives in ``config/*.yaml``, never in the code or
on the command line. ``@stx.session`` loads ``./config/*.yaml`` (relative to
the working directory) into the injected ``CONFIG``: the file stem becomes
the namespace and keys are upper-cased, so ``config/ANALYSIS.yaml`` with
``N_SAMPLES: 100`` is read as ``CONFIG.ANALYSIS.N_SAMPLES``. The CLI is
for non-numeric inputs such as ``--data-path``.

Run (from this directory, so ./config/ is found):
    python 01_session.py
    python 01_session.py --data-path measured.csv   # CSV with a "y" column
    python 01_session.py --help                     # lists CONFIG.ANALYSIS.*

To change a parameter, edit config/ANALYSIS.yaml. Each run freezes the
values it used in CONFIGS/CONFIG.yaml.

Output:
    01_session_out/
    ├── sine.png, sine.yaml, sine_data/*.csv   # figure, recipe, plotted data
    └── FINISHED_SUCCESS/<session_id>/
        ├── CONFIGS/CONFIG.yaml                # incl. the ANALYSIS values used
        └── logs/{stdout,stderr}.log
"""

import numpy as np

import scitex as stx


@stx.session
def main(
    data_path: str = None,  # --data-path measured.csv (optional input file)
    CONFIG=stx.session.INJECTED,  # ./config/*.yaml aggregated
    COLORS=stx.session.INJECTED,  # Color palette
    plt=stx.session.INJECTED,  # Pre-configured matplotlib
    rngg=stx.session.INJECTED,  # Seeded random generators
    logger=stx.session.INJECTED,  # Session logger
):
    """Plot a noisy sine wave; parameters come from config/ANALYSIS.yaml."""
    params = CONFIG.ANALYSIS
    logger.info(f"Session ID: {CONFIG.ID}")
    logger.info(f"Output dir: {CONFIG.SDIR_RUN}")
    logger.info(f"N_SAMPLES={params.N_SAMPLES}, NOISE_STD={params.NOISE_STD}")

    if data_path:
        y = stx.io.load(data_path)["y"].to_numpy()
        x = np.arange(len(y))
    else:
        x = np.linspace(0, 2 * np.pi, params.N_SAMPLES)
        noise = rngg("noise").normal(0, params.NOISE_STD, params.N_SAMPLES)
        y = np.sin(x) + noise

    # Plot with figrecipe (plotted data is tracked for the CSV export)
    fig, ax = stx.plt.subplots()
    ax.plot(x, y)
    ax.set_xyt("Time", "Amplitude", f"Sine Wave (n={len(y)})")

    # Save figure (also writes the sine.yaml recipe + sine_data/*.csv)
    stx.io.save(fig, "sine.png")

    logger.info("Done")
    return 0


if __name__ == "__main__":
    main()
