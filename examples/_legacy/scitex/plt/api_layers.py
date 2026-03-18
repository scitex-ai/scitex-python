#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-12-13 10:06:12 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex-code/examples/plt/api_layers.py


"""Demo: SciTeX Plotting API Layers.

Uses scitex.dev.plt registries to demonstrate all three API layers:
- PLOTTERS_STX: stx_* methods (ArrayLike input, tracked)
- PLOTTERS_SNS: sns_* methods (DataFrame input, tracked)
- PLOTTERS_MPL: mpl_* methods (matplotlib-style, tracked)

All three layers produce CSV/JSON output for reproducibility.
"""

import scitex as stx
from scitex.dev.plt import PLOTTERS_STX
from scitex.dev.plt import PLOTTERS_SNS
from scitex.dev.plt import PLOTTERS_MPL

OUTPUT_DIR = "./api_layers_out"


@stx.session
def main(
    extension="png",
    plt=stx.session.INJECTED,
    rngg=stx.session.INJECTED,
    logger=stx.session.INJECTED,
):
    """Demo: All registered plotters by API layer."""
    rng = rng("api_layers_demo")

    logger.info("=" * 60)
    logger.info("SciTeX API Layers Demo")
    logger.info("=" * 60)

    total = 0

    # stx_* API Layer (ArrayLike input)
    logger.info(
        f"\n[PLOTTERS_STX] {len(PLOTTERS_STX)} stx_* methods (ArrayLike)"
    )
    for name, plotter in PLOTTERS_STX.items():
        total += 1
        logger.info(f"  [{total:02d}] {name}")
        try:
            fig, ax = plotter(plt, rng)
            stx.io.save(fig, f"{OUTPUT_DIR}/{name}.{extension}")
            fig.close()
        except Exception as e:
            logger.warning(f"    Failed: {e}")

    # sns_* API Layer (DataFrame input)
    logger.info(
        f"\n[PLOTTERS_SNS] {len(PLOTTERS_SNS)} sns_* methods (DataFrame)"
    )
    for name, plotter in PLOTTERS_SNS.items():
        total += 1
        logger.info(f"  [{total:02d}] {name}")
        try:
            fig, ax = plotter(plt, rng)
            stx.io.save(fig, f"{OUTPUT_DIR}/{name}.{extension}")
            fig.close()
        except Exception as e:
            logger.warning(f"    Failed: {e}")

    # mpl_* API Layer (matplotlib-style)
    logger.info(
        f"\n[PLOTTERS_MPL] {len(PLOTTERS_MPL)} mpl_* methods (matplotlib-style)"
    )
    for name, plotter in PLOTTERS_MPL.items():
        total += 1
        logger.info(f"  [{total:02d}] {name}")
        try:
            fig, ax = plotter(plt, rng)
            stx.io.save(fig, f"{OUTPUT_DIR}/{name}.{extension}")
            fig.close()
        except Exception as e:
            logger.warning(f"    Failed: {e}")

    logger.info("\n" + "=" * 60)
    logger.info(f"Completed {total} plotters")
    logger.info("=" * 60)

    return 0


if __name__ == "__main__":
    main()

# EOF
