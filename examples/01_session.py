#!/usr/bin/env python3
"""Example: @stx.session -- Reproducible Experiment Tracking

Run:
    python 01_session.py input.csv
    python 01_session.py input.csv --n-samples 200 --learning-rate 0.01
    python 01_session.py --help

Output:
    01_session_out/FINISHED_SUCCESS/<timestamp>/
    ├── sine.png, sine.csv
    ├── CONFIGS/CONFIG.yaml
    └── logs/{stdout,stderr}.log
"""

import numpy as np

import scitex as stx


@stx.session
def main(
    data_path,  # Positional: python 01_session.py data.csv
    n_samples=100,  # Keyword:    --n-samples 200
    learning_rate=0.001,  # Keyword:    --learning-rate 0.01
    CONFIG=stx.session.INJECTED,  # ./config/*.yaml aggregated
    COLORS=stx.session.INJECTED,  # Color palette
    plt=stx.session.INJECTED,  # Pre-configured matplotlib
    rngg=stx.session.INJECTED,  # Random number generator (global)
    logger=stx.session.INJECTED,  # Session logger
):
    """Demonstrate @stx.session with auto-CLI and config injection."""
    # Log session info
    logger.info(f"Session ID: {CONFIG.ID}")
    logger.info(f"Output dir: {CONFIG.SDIR_RUN}")
    logger.info(f"Data path: {data_path}")
    logger.info(f"n_samples={n_samples}, lr={learning_rate}")

    # Generate demo data
    x = np.linspace(0, 2 * np.pi, n_samples)
    y = np.sin(x) + np.random.randn(n_samples) * 0.1

    # Plot with figrecipe (injected plt)
    fig, ax = stx.plt.subplots()
    ax.plot_line(x, y)
    ax.set_xyt("Time", "Amplitude", f"Sine Wave (n={n_samples})")

    # Save figure (auto-exports sine.png + sine.csv)
    stx.io.save(fig, "sine.png")

    # Save parameters
    stx.io.save(
        {"n_samples": n_samples, "learning_rate": learning_rate},
        "params.yaml",
    )

    logger.info("Done")
    return 0


if __name__ == "__main__":
    main()
