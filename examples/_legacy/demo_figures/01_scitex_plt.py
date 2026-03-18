#!/usr/bin/env python3
"""Demo: scitex.plt example figures with SCITEX_THEME colors."""

import numpy as np

import scitex as stx
from scitex.plt.color import PARAMS

# Get theme colors
COLORS = PARAMS["RGBA_NORM_FOR_CYCLE"]

OUTPUT_DIR = "/home/ywatanabe/proj/scitex-code/examples/demo_figures"


@stx.session
def demo_line_plot(plt=stx.INJECTED, logger=stx.INJECTED):
    """Simple line plot with multiple traces."""
    fig, ax = plt.subplots()

    x = np.linspace(0, 2 * np.pi, 100)
    for i, (name, color) in enumerate(list(COLORS.items())[:4]):
        y = np.sin(x + i * 0.5) * (1 - i * 0.15)
        ax.plot(x, y, color=color[:3], label=name, linewidth=1.5)

    ax.set_xlabel("Phase [rad]")
    ax.set_ylabel("Amplitude [-]")
    ax.set_title("Sinusoidal Waves")
    ax.legend()

    stx.io.save(fig, f"{OUTPUT_DIR}/01_line_plot.png")
    logger.info("Saved: 01_line_plot.png")
    plt.close(fig)


@stx.session
def demo_scatter_plot(plt=stx.INJECTED, rngg=stx.INJECTED, logger=stx.INJECTED):
    """Scatter plot with color-coded groups."""
    rng = rng("scatter")
    fig, ax = plt.subplots()

    groups = ["blue", "red", "green", "yellow"]

    for i, group in enumerate(groups):
        x = rng.standard_normal(30) + i * 2
        y = rng.standard_normal(30) + i * 0.5
        color = COLORS[group][:3]
        ax.scatter(x, y, c=[color], label=group, s=30, alpha=0.7)

    ax.set_xlabel("Feature 1 [-]")
    ax.set_ylabel("Feature 2 [-]")
    ax.set_title("Cluster Analysis")
    ax.legend()

    stx.io.save(fig, f"{OUTPUT_DIR}/02_scatter_plot.png")
    logger.info("Saved: 02_scatter_plot.png")
    plt.close(fig)


@stx.session
def demo_bar_plot(plt=stx.INJECTED, logger=stx.INJECTED):
    """Bar plot with error bars."""
    fig, ax = plt.subplots()

    categories = ["A", "B", "C", "D"]
    values = [4.2, 3.8, 5.1, 4.5]
    errors = [0.3, 0.4, 0.35, 0.25]
    colors = [COLORS[c][:3] for c in ["blue", "red", "green", "yellow"]]

    ax.bar(categories, values, color=colors, edgecolor="black", linewidth=0.5)
    ax.errorbar(
        categories,
        values,
        yerr=errors,
        fmt="none",
        ecolor="black",
        capsize=3,
        linewidth=1,
    )

    ax.set_xlabel("Group [-]")
    ax.set_ylabel("Performance [-]")
    ax.set_title("Group Comparison")

    stx.io.save(fig, f"{OUTPUT_DIR}/03_bar_plot.png")
    logger.info("Saved: 03_bar_plot.png")
    plt.close(fig)


@stx.session
def demo_heatmap(plt=stx.INJECTED, rngg=stx.INJECTED, logger=stx.INJECTED):
    """Correlation heatmap."""
    rng = rng("heatmap")
    fig, ax = plt.subplots()

    data = rng.standard_normal((5, 5))
    data = (data + data.T) / 2  # Make symmetric
    np.fill_diagonal(data, 1)

    im = ax.imshow(data, cmap="RdBu_r", vmin=-1, vmax=1)

    # Add colorbar
    cbar = fig.colorbar(im, ax=ax, shrink=0.8)
    cbar.set_label("Correlation [-]")

    # Labels
    labels = ["Var1", "Var2", "Var3", "Var4", "Var5"]
    ax.set_xticks(range(5))
    ax.set_yticks(range(5))
    ax.set_xticklabels(labels, rotation=45, ha="right")
    ax.set_yticklabels(labels)
    ax.set_title("Correlation Matrix")

    stx.io.save(fig, f"{OUTPUT_DIR}/04_heatmap.png")
    logger.info("Saved: 04_heatmap.png")
    plt.close(fig)


@stx.session
def demo_histogram(plt=stx.INJECTED, rngg=stx.INJECTED, logger=stx.INJECTED):
    """Histogram with distribution overlay."""
    rng = rng("histogram")
    fig, ax = plt.subplots()

    data1 = rng.normal(0, 1, 500)
    data2 = rng.normal(2, 1.2, 500)

    ax.hist(
        data1,
        bins=30,
        alpha=0.6,
        color=COLORS["blue"][:3],
        label="Control",
        edgecolor="white",
        linewidth=0.5,
    )
    ax.hist(
        data2,
        bins=30,
        alpha=0.6,
        color=COLORS["red"][:3],
        label="Treatment",
        edgecolor="white",
        linewidth=0.5,
    )

    ax.set_xlabel("Value [-]")
    ax.set_ylabel("Count [-]")
    ax.set_title("Distribution Comparison")
    ax.legend()

    stx.io.save(fig, f"{OUTPUT_DIR}/05_histogram.png")
    logger.info("Saved: 05_histogram.png")
    plt.close(fig)


@stx.session
def demo_boxplot(plt=stx.INJECTED, rngg=stx.INJECTED, logger=stx.INJECTED):
    """Box plot comparison."""
    rng = rng("boxplot")
    fig, ax = plt.subplots()

    data = [rng.normal(m, 0.5, 50) for m in [2, 3, 2.5, 4]]

    bp = ax.boxplot(data, patch_artist=True, tick_labels=["A", "B", "C", "D"])

    colors = [COLORS[c][:3] for c in ["blue", "red", "green", "yellow"]]
    for patch, color in zip(bp["boxes"], colors):
        patch.set_facecolor(color)
        patch.set_alpha(0.7)

    ax.set_xlabel("Group [-]")
    ax.set_ylabel("Measurement [-]")
    ax.set_title("Box Plot Comparison")

    stx.io.save(fig, f"{OUTPUT_DIR}/06_boxplot.png")
    logger.info("Saved: 06_boxplot.png")
    plt.close(fig)


@stx.session
def demo_subplots_grid(plt=stx.INJECTED, rngg=stx.INJECTED, logger=stx.INJECTED):
    """2x2 subplot grid."""
    rng = rng("subplots")
    fig, axes = plt.subplots(nrows=2, ncols=2)

    x = np.linspace(0, 10, 100)

    # Top-left: Line
    axes[0, 0].plot(x, np.sin(x), color=COLORS["blue"][:3])
    axes[0, 0].set_title("Sine Wave")

    # Top-right: Scatter
    axes[0, 1].scatter(
        rng.standard_normal(50),
        rng.standard_normal(50),
        c=[COLORS["red"][:3]],
        s=20,
        alpha=0.6,
    )
    axes[0, 1].set_title("Random Points")

    # Bottom-left: Bar
    axes[1, 0].bar(
        [1, 2, 3, 4],
        [3, 7, 2, 5],
        color=[COLORS[c][:3] for c in ["blue", "red", "green", "yellow"]],
    )
    axes[1, 0].set_title("Bar Chart")

    # Bottom-right: Histogram
    axes[1, 1].hist(
        rng.standard_normal(200),
        bins=20,
        color=COLORS["purple"][:3],
        edgecolor="white",
        linewidth=0.5,
    )
    axes[1, 1].set_title("Histogram")

    fig.tight_layout()
    stx.io.save(fig, f"{OUTPUT_DIR}/07_subplots_grid.png")
    logger.info("Saved: 07_subplots_grid.png")
    plt.close(fig)


@stx.session
def demo_shaded_errorband(
    plt=stx.INJECTED, rngg=stx.INJECTED, logger=stx.INJECTED
):
    """Line plot with shaded error band."""
    rng = rng("errorband")
    fig, ax = plt.subplots()

    x = np.linspace(0, 10, 50)
    y = np.sin(x) + 0.5 * x
    yerr = 0.3 + 0.1 * rng.standard_normal(50)

    ax.fill_between(x, y - yerr, y + yerr, alpha=0.3, color=COLORS["blue"][:3])
    ax.plot(x, y, color=COLORS["blue"][:3], linewidth=1.5, label="Mean ± SEM")

    ax.set_xlabel("Time [s]")
    ax.set_ylabel("Response [-]")
    ax.set_title("Time Series with Error Band")
    ax.legend()

    stx.io.save(fig, f"{OUTPUT_DIR}/08_shaded_errorband.png")
    logger.info("Saved: 08_shaded_errorband.png")
    plt.close(fig)


if __name__ == "__main__":
    print("Generating scitex.plt demo figures...")
    print(f"Output directory: {OUTPUT_DIR}")
    print("-" * 40)

    demo_line_plot()
    demo_scatter_plot()
    demo_bar_plot()
    demo_heatmap()
    demo_histogram()
    demo_boxplot()
    demo_subplots_grid()
    demo_shaded_errorband()

    print("-" * 40)
    print("Done! All figures saved.")
