#!/usr/bin/env python3
# Timestamp: "2026-02-12 09:25:00 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex-python/examples/scitex/io/schematic_io_concept.py

"""stx.io concept schematic: Transparent Verification Layer.

Shows how unified I/O captures hashes at every boundary,
writing to verification.db (SQLite) in real-time.
The dependency DAG is reconstructed from the DB on demand.
For paper Figure 02 Panel A.
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
    """Generate stx.io concept schematic."""
    out = Path(CONFIG.SDIR_OUT)

    W, H = 170, 150
    s = fr.Schematic(
        title="stx.io: Transparent Verification Layer",
        width_mm=W,
        height_mm=H,
    )

    # --- Row 1: Research Code -> stx.io -> File Formats ---
    bw, bh = 38, 26
    row1_cy = H - 28

    s.add_box(
        "code",
        "Research Code",
        content=["stx.io.load(path)", "stx.io.save(obj, path)"],
        x_mm=28,
        y_mm=row1_cy,
        width_mm=bw,
        height_mm=bh,
    )
    s.add_box(
        "stxio",
        "stx.io",
        subtitle="Unified API",
        content=["Single entry point"],
        emphasis="success",
        x_mm=W / 2,
        y_mm=row1_cy,
        width_mm=bw,
        height_mm=bh,
    )
    s.add_box(
        "formats",
        "50+ Formats",
        subtitle="CSV, NPY, HDF5, EEG, ...",
        x_mm=W - 28,
        y_mm=row1_cy,
        width_mm=bw,
        height_mm=bh,
    )

    # Arrows Row 1
    s.add_arrow("code", "stxio", label="load / save")
    s.add_arrow("stxio", "formats", label="Dispatch")

    # --- Row 2: Verification Hooks ---
    hook_w, hook_h = 48, 26
    row2_cy = H / 2 + 8

    s.add_box(
        "on_load",
        "on_io_load()",
        subtitle="Verification Hook",
        content=["Record input hash", "Detect parent session"],
        emphasis="warning",
        x_mm=W / 2 - hook_w / 2 - 10,
        y_mm=row2_cy,
        width_mm=hook_w,
        height_mm=hook_h,
    )
    s.add_box(
        "on_save",
        "on_io_save()",
        subtitle="Verification Hook",
        content=["Record output hash"],
        emphasis="warning",
        x_mm=W / 2 + hook_w / 2 + 10,
        y_mm=row2_cy,
        width_mm=hook_w,
        height_mm=hook_h,
    )

    # Arrows from stx.io down to hooks
    s.add_arrow("stxio", "on_load", color="orange", style="dashed")
    s.add_arrow("stxio", "on_save", color="orange", style="dashed")

    # --- Row 3: verification.db + Dependency DAG ---
    row3_cy = 18
    db_w, db_h = 46, 22

    s.add_box(
        "db",
        "verification.db",
        subtitle="SQLite",
        content=["runs, file_hashes"],
        emphasis="red",
        x_mm=W / 2 - db_w / 2 - 10,
        y_mm=row3_cy,
        width_mm=db_w,
        height_mm=db_h,
    )
    s.add_box(
        "dag",
        "Dependency DAG",
        subtitle="Reconstructed on demand",
        emphasis="success",
        x_mm=W / 2 + db_w / 2 + 10,
        y_mm=row3_cy,
        width_mm=db_w,
        height_mm=db_h,
    )

    # Arrows from hooks to DB, DB to DAG
    s.add_arrow("on_load", "db", color="red")
    s.add_arrow("on_save", "db", color="red")
    s.add_arrow("db", "dag", label="Query", color="green")

    # Render
    fig, ax = fr.subplots()
    ax.schematic(s, id="stx_io_concept")
    fr.save(fig, out / "stx_io_concept.png", validate=False)

    logger.info(f"Saved to: {out}/stx_io_concept.png")
    return 0


if __name__ == "__main__":
    main()

# EOF
