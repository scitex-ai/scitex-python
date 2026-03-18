#!/usr/bin/env python3
# Timestamp: "2026-02-12 09:15:00 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex-python/examples/scitex/decorators/schematic_session_concept.py

"""@stx.session concept schematic: Structured Research Units.

Shows how the session decorator structures research into discrete
verifiable units with automatic hash computation.
For paper Figure 02 Panel B.
NOTE: x_mm/y_mm is the CENTER of the box, not bottom-left.
"""

import matplotlib

matplotlib.use("Agg")

from pathlib import Path

import figrecipe as fr

import scitex as stx


@stx.session
def main(
    CONFIG=stx.session.INJECTED,
    logger=stx.session.INJECTED,
):
    """Generate @stx.session concept schematic."""
    out = Path(CONFIG.SDIR_OUT)

    W, H = 170, 130
    s = fr.Schematic(
        title="@stx.session: Structured Research Units",
        width_mm=W,
        height_mm=H,
    )

    # --- Row 1: The Decorator ---
    row1_cy = H - 28
    s.add_box(
        "decorator",
        "@stx.session",
        subtitle="Decorator",
        content=["Transforms function", "into research unit"],
        emphasis="purple",
        x_mm=W / 2,
        y_mm=row1_cy,
        width_mm=44,
        height_mm=26,
    )

    # --- Row 2: Three hashed inputs (no container) ---
    iw, ih = 36, 24
    row2_cy = H / 2 + 2

    s.add_box(
        "inputs",
        "Input Files",
        subtitle="SHA-256 hash",
        emphasis="success",
        x_mm=W / 2 - iw - 8,
        y_mm=row2_cy,
        width_mm=iw,
        height_mm=ih,
    )
    s.add_box(
        "script",
        "Script Code",
        subtitle="AST-normalized hash",
        emphasis="success",
        x_mm=W / 2,
        y_mm=row2_cy,
        width_mm=iw,
        height_mm=ih,
    )
    s.add_box(
        "environ",
        "Environment",
        subtitle="Python + packages",
        emphasis="success",
        x_mm=W / 2 + iw + 8,
        y_mm=row2_cy,
        width_mm=iw,
        height_mm=ih,
    )

    # Arrows from decorator to inputs (on_session_start)
    s.add_arrow("decorator", "inputs", color="green")
    s.add_arrow("decorator", "script", color="green")
    s.add_arrow("decorator", "environ", color="green")

    # --- Row 3: Output + Verification Record ---
    ow, oh = 44, 26
    row3_cy = 22

    s.add_box(
        "outputs",
        "Session Outputs",
        subtitle="script_out/<ID>/",
        content=["SHA-256 hashes"],
        emphasis="warning",
        x_mm=W / 2 - ow / 2 - 12,
        y_mm=row3_cy,
        width_mm=ow,
        height_mm=oh,
    )
    s.add_box(
        "verify",
        "verify.json",
        subtitle="Verification Record",
        content=["Combined hash"],
        emphasis="red",
        x_mm=W / 2 + ow / 2 + 12,
        y_mm=row3_cy,
        width_mm=ow,
        height_mm=oh,
    )

    # Arrows from inputs to outputs
    s.add_arrow("inputs", "outputs", color="orange")
    s.add_arrow("script", "outputs", color="orange")
    s.add_arrow("environ", "verify", color="red", style="dashed")
    s.add_arrow("outputs", "verify", label="close", color="red")

    # Render
    fig, ax = fr.subplots()
    ax.schematic(s, id="stx_session_concept")
    fr.save(fig, out / "stx_session_concept.png", validate=False)

    logger.info(f"Saved to: {out}/stx_session_concept.png")
    return 0


if __name__ == "__main__":
    main()

# EOF
