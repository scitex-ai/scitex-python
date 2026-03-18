#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: 2025-12-14
# File: /home/ywatanabe/proj/scitex-code/examples/scitex/fig/gui_editors.py
"""
Demo: Interactive GUI Figure Editor

Launch interactive editor for figure editing:
    ./gui_editors.py                         # Default: complex multi-panel figure
    ./gui_editors.py -f complex              # Complex: 6 panels, multi-axes, various types
    ./gui_editors.py -f stx_scatter          # Single panel with specific plot type
    ./gui_editors.py -f stx_heatmap          # Single panel with heatmap

For programmatic (non-GUI) editing, see cui_editor.py

Install GUI backends: pip install scitex[gui]
"""

from pathlib import Path
from typing import Literal

import numpy as np

import scitex as stx
from scitex.dev.plt import PLOTTERS

# Type alias for figure choices - shows available options in help
FigureType = Literal[
    # Special: Complex multi-panel demo
    "complex",
    # stx_* (25 plotters)
    "stx_line",
    "stx_mean_std",
    "stx_mean_ci",
    "stx_median_iqr",
    "stx_shaded_line",
    "stx_box",
    "stx_violin",
    "stx_scatter",
    "stx_bar",
    "stx_barh",
    "stx_errorbar",
    "stx_fill_between",
    "stx_kde",
    "stx_ecdf",
    "stx_heatmap",
    "stx_image",
    "stx_imshow",
    "stx_contour",
    "stx_raster",
    "stx_conf_mat",
    "stx_joyplot",
    "stx_rectangle",
    "stx_fillv",
    "stx_boxplot",
    "stx_violinplot",
    # sns_* (10 plotters)
    "sns_boxplot",
    "sns_violinplot",
    "sns_barplot",
    "sns_histplot",
    "sns_kdeplot",
    "sns_scatterplot",
    "sns_lineplot",
    "sns_swarmplot",
    "sns_stripplot",
    "sns_heatmap",
    # mpl_* (26 plotters)
    "mpl_plot",
    "mpl_scatter",
    "mpl_bar",
    "mpl_barh",
    "mpl_hist",
    "mpl_hist2d",
    "mpl_hexbin",
    "mpl_boxplot",
    "mpl_violinplot",
    "mpl_errorbar",
    "mpl_step",
    "mpl_stem",
    "mpl_fill",
    "mpl_fill_between",
    "mpl_stackplot",
    "mpl_contour",
    "mpl_contourf",
    "mpl_imshow",
    "mpl_pcolormesh",
    "mpl_pie",
    "mpl_eventplot",
    "mpl_quiver",
    "mpl_axhline",
    "mpl_axvline",
    "mpl_axhspan",
    "mpl_axvspan",
]


def create_complex_figure(output_dir: Path, plt, rng, COLORS) -> Path:
    """Create a complex multi-panel figure with various plot types and multi-axes.

    Layout (2x3 grid):
        A: Line + twinx (dual y-axis)
        B: Scatter with colorbar
        C: Heatmap
        D: Bar chart with error bars
        E: Multi-line with fill_between
        F: Violin + box overlay
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    panels = {}

    # Panel A: Line plot with dual y-axis (twinx)
    fig_a, ax_a = plt.subplots(figsize=(4, 3))
    x = np.linspace(0, 10, 100)
    y1 = np.sin(x) + rng.normal(0, 0.1, 100)
    y2 = np.exp(x / 5) + rng.normal(0, 0.5, 100)
    ax_a.plot(x, y1, color=COLORS.blue, label="sin(x)", linewidth=2)
    ax_a.set_xlabel("Time (s)")
    ax_a.set_ylabel("Amplitude")
    ax_a.yaxis.label.set_color(COLORS.blue)
    ax_a.tick_params(axis="y", labelcolor=COLORS.blue)
    ax_a2 = ax_a.twinx()
    ax_a2.plot(
        x, y2, color=COLORS.orange, label="exp(x/5)", linewidth=2, linestyle="--"
    )
    ax_a2.set_ylabel("Growth")
    ax_a2.yaxis.label.set_color(COLORS.orange)
    ax_a2.tick_params(axis="y", labelcolor=COLORS.orange)
    ax_a.set_title("Dual Y-Axis: Signal & Growth")
    lines1, labels1 = ax_a.get_legend_handles_labels()
    lines2, labels2 = ax_a2.get_legend_handles_labels()
    ax_a.legend(lines1 + lines2, labels1 + labels2, loc="lower right", framealpha=0.9)
    plot_a = output_dir / "panel_A_twinx.plot"
    stx.io.save(fig_a, plot_a, dpi=150)
    plt.close(fig_a)
    panels["A"] = str(plot_a)

    # Panel B: Scatter with colorbar
    fig_b, ax_b = plt.subplots(figsize=(4, 3))
    n = 200
    x_scatter = rng.normal(0, 1, n)
    y_scatter = rng.normal(0, 1, n)
    colors = np.sqrt(x_scatter**2 + y_scatter**2)
    sizes = 50 + 100 * rng.random(n)
    sc = ax_b.scatter(
        x_scatter, y_scatter, c=colors, s=sizes, cmap="viridis", alpha=0.7
    )
    fig_b.colorbar(sc, ax=ax_b, label="Distance from origin")
    ax_b.set_xlabel("X")
    ax_b.set_ylabel("Y")
    ax_b.set_title("Scatter: Size & Color Encoding")
    ax_b.axhline(0, color=COLORS.gray, linewidth=0.5, linestyle="--")
    ax_b.axvline(0, color=COLORS.gray, linewidth=0.5, linestyle="--")
    plot_b = output_dir / "panel_B_scatter.plot"
    stx.io.save(fig_b, plot_b, dpi=150)
    plt.close(fig_b)
    panels["B"] = str(plot_b)

    # Panel C: Heatmap with annotations
    fig_c, ax_c = plt.subplots(figsize=(4, 3))
    data_heatmap = rng.normal(0, 1, (8, 10))
    im = ax_c.imshow(data_heatmap, cmap="RdBu_r", aspect="auto")
    fig_c.colorbar(im, ax=ax_c, label="Value")
    ax_c.set_xlabel("Condition")
    ax_c.set_ylabel("Sample")
    ax_c.set_title("Heatmap: Correlation Matrix")
    ax_c.set_xticks(range(10))
    ax_c.set_yticks(range(8))
    ax_c.set_xticklabels([f"C{i}" for i in range(10)], fontsize=7)
    ax_c.set_yticklabels([f"S{i}" for i in range(8)], fontsize=7)
    plot_c = output_dir / "panel_C_heatmap.plot"
    stx.io.save(fig_c, plot_c, dpi=150)
    plt.close(fig_c)
    panels["C"] = str(plot_c)

    # Panel D: Bar chart with error bars
    fig_d, ax_d = plt.subplots(figsize=(4, 3))
    categories = ["A", "B", "C", "D", "E"]
    values = [3.2, 4.1, 2.8, 5.5, 4.0]
    errors = [0.3, 0.5, 0.4, 0.6, 0.35]
    bar_colors = [COLORS.blue, COLORS.green, COLORS.orange, COLORS.purple, COLORS.red]
    bars = ax_d.bar(
        categories,
        values,
        yerr=errors,
        capsize=5,
        color=bar_colors,
        edgecolor=COLORS.black,
    )
    ax_d.set_xlabel("Category")
    ax_d.set_ylabel("Value")
    ax_d.set_title("Bar Chart: Comparison with Error")
    ax_d.axhline(np.mean(values), color=COLORS.red, linestyle="--", label="Mean")
    ax_d.legend()
    plot_d = output_dir / "panel_D_bar.plot"
    stx.io.save(fig_d, plot_d, dpi=150)
    plt.close(fig_d)
    panels["D"] = str(plot_d)

    # Panel E: Multi-line with confidence interval
    fig_e, ax_e = plt.subplots(figsize=(4, 3))
    x_line = np.linspace(0, 2 * np.pi, 50)
    line_colors = [COLORS.blue, COLORS.green, COLORS.orange]
    for i, (name, offset) in enumerate([("Alpha", 0), ("Beta", 1), ("Gamma", 2)]):
        y_mean = np.sin(x_line + offset)
        y_std = 0.15 + 0.05 * i
        ax_e.plot(x_line, y_mean, label=name, linewidth=2, color=line_colors[i])
        ax_e.fill_between(
            x_line, y_mean - y_std, y_mean + y_std, alpha=0.3, color=line_colors[i]
        )
    ax_e.set_xlabel("Phase")
    ax_e.set_ylabel("Amplitude")
    ax_e.set_title("Multi-Line: Mean ± CI")
    ax_e.legend(loc="upper right")
    ax_e.set_xlim(0, 2 * np.pi)
    plot_e = output_dir / "panel_E_multiline.plot"
    stx.io.save(fig_e, plot_e, dpi=150)
    plt.close(fig_e)
    panels["E"] = str(plot_e)

    # Panel F: Violin + box overlay (subplots)
    fig_f, (ax_f1, ax_f2) = plt.subplots(1, 2, figsize=(4, 3), sharey=True)
    data_violin = [
        rng.normal(0, 1, 50),
        rng.normal(1, 1.5, 50),
        rng.normal(-0.5, 0.8, 50),
    ]
    violin_colors = [COLORS.blue, COLORS.green, COLORS.orange]
    vp = ax_f1.violinplot(data_violin, showmeans=True, showmedians=False)
    for i, body in enumerate(vp["bodies"]):
        body.set_facecolor(violin_colors[i])
        body.set_alpha(0.7)
    ax_f1.set_xlabel("Group")
    ax_f1.set_ylabel("Value")
    ax_f1.set_title("Violin")
    ax_f1.set_xticks([1, 2, 3])
    ax_f1.set_xticklabels(["G1", "G2", "G3"])
    bp = ax_f2.boxplot(data_violin, patch_artist=True)
    for i, patch in enumerate(bp["boxes"]):
        patch.set_facecolor(violin_colors[i])
        patch.set_alpha(0.7)
    ax_f2.set_xlabel("Group")
    ax_f2.set_title("Box")
    ax_f2.set_xticks([1, 2, 3])
    ax_f2.set_xticklabels(["G1", "G2", "G3"])
    fig_f.suptitle("Distribution: Violin vs Box", fontsize=10, y=0.98)
    fig_f.tight_layout()
    plot_f = output_dir / "panel_F_distribution.plot"
    stx.io.save(fig_f, plot_f, dpi=150)
    plt.close(fig_f)
    panels["F"] = str(plot_f)

    # Create figz bundle
    figure_path = output_dir / "Figure_Complex.figure"
    stx.fig.save_figz(panels, figure_path)

    return figure_path


def create_sample_figure(
    output_dir: Path,
    plt,
    rng,
    figure_type: str = "complex",
    COLORS=None,
) -> Path:
    """Create a sample figure as .figure bundle for editing."""
    output_dir.mkdir(parents=True, exist_ok=True)

    # Handle complex multi-panel figure
    if figure_type == "complex":
        return create_complex_figure(output_dir, plt, rng, COLORS)

    # Get the plotter function
    if figure_type not in PLOTTERS:
        available = ", ".join(sorted(PLOTTERS.keys())[:10]) + "..."
        raise ValueError(
            f"Unknown figure type: {figure_type}. " f"Available: {available}"
        )

    plotter = PLOTTERS[figure_type]

    # Create the figure
    fig, ax = plotter(plt, rng)

    # Save as pltz (zip format)
    plot_path = output_dir / f"panel_A_{figure_type}.plot"
    stx.io.save(fig, plot_path, dpi=150)
    plt.close(fig)

    # Create figz bundle with single panel (zip format)
    figure_path = output_dir / f"Figure_{figure_type}.figure"
    panels = {"A": str(plot_path)}
    stx.fig.save_figz(panels, figure_path)

    return figure_path


# Type alias for backend choices
Backend = Literal["auto", "flask", "dearpygui", "qt", "tkinter", "mpl"]


@stx.session
def main(
    figure: FigureType = "complex",
    backend: Backend = "flask",
    CONFIG=stx.session.INJECTED,
    plt=stx.session.INJECTED,
    COLORS=stx.session.INJECTED,
    rngg=stx.session.INJECTED,
    logger=stx.session.INJECTED,
):
    """Launch interactive GUI editor.

    Args:
        figure: complex (6-panel demo), or single plotter name (stx_*, sns_*, mpl_*)
        backend: GUI backend (flask recommended)
    """
    out = Path(CONFIG.SDIR_OUT)
    rng = rng("gui_editors_demo")

    logger.info("=" * 60)
    logger.info("GUI Figure Editor Demo")
    logger.info("=" * 60)

    # Create sample figure as figz bundle
    logger.info(f"\nCreating sample figz bundle for: {figure}")
    bundle_path = create_sample_figure(out, plt, rng, figure, COLORS)
    logger.success(f"Figz bundle created: {bundle_path}")

    # List bundle contents
    logger.info("\nFigz bundle contents:")
    if bundle_path.is_file() and str(bundle_path).endswith(".figure"):
        # ZIP format: use zipfile to list contents
        import zipfile

        with zipfile.ZipFile(bundle_path, "r") as zf:
            for name in sorted(zf.namelist())[:10]:  # Show first 10 entries
                logger.info(f"  {name}")
            if len(zf.namelist()) > 10:
                logger.info(f"  ... and {len(zf.namelist()) - 10} more files")
    elif bundle_path.is_dir():
        # Directory format
        for f in sorted(bundle_path.iterdir()):
            if f.is_dir():
                logger.info(f"  {f.name}/")
            else:
                logger.info(f"  {f.name}")

    # Launch interactive editor
    logger.info("\nLaunching Flask editor...")
    logger.info("(Close the browser tab to exit)")
    logger.info("=" * 60)

    # Launch the GUI editor
    stx.fig.edit(str(bundle_path), backend=backend)


if __name__ == "__main__":
    main()

# EOF
