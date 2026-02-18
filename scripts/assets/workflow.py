#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2026-02-16 12:40:23 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex-python/scripts/assets/workflow.py


"""Generate SciTeX overview diagram using figrecipe.diagram."""

from figrecipe._diagram import Diagram

import scitex as stx


def _add_input_boxes(d, C, CT):
    d.add_box(
        "scripts_box", "Python Script", shape="document", emphasis="muted"
    )
    d.add_box(
        "linter_box",
        "Automatic translation",
        subtitle="Smooth Migration to SciTeX",
        content=["scitex.linter"],
        padding_mm=8,
        fill_color=CT["orange"],
        border_color=C["orange"],
        width_mm=50,
    )
    d.add_box("source_box", "Source Data", shape="cylinder", height_mm=40)


def _add_analysis_boxes(d, C, CT):
    d.add_box(
        "core_box",
        "Core Modules",
        subtitle="Infrastructure of All Python Scripts in SciTeX",
        content=[
            "@scitex.session",
            "scitex.plt",
            "(figrecipe)",
            "scitex.stats",
            "scitex.io",
            "scitex.config",
            "scitex.logger",
            "scitex.repro",
            "scitex.rng",
            "scitex.template",
        ],
        fill_color=CT["blue"],
        border_color=C["blue"],
        bullet="circle",
    )
    d.add_box(
        "domain_box",
        "Domain-specific Modules",
        subtitle="Calculation Modules for Specific Fields",
        content=["scitex.dsp", "scitex.ml", "scitex.nn"],
        fill_color=CT["navy"],
        border_color=C["navy"],
        bullet="circle",
    )


def _add_publication_boxes(d, C, CT):
    d.add_box(
        "writer_box",
        "Writer",
        subtitle="LaTeX Compilation",
        content=[
            "scitex.writer",
            "Direct Link with bibliography, figures, and tables",
        ],
        fill_color=CT["brown"],
        border_color=C["brown"],
        bullet="circle",
    )
    d.add_box(
        "outputs_box",
        "Outputs",
        subtitle="Artifacts from Analysis",
        content=[
            "Processed Data",
            "Intermediate Results",
            "Statistical Results",
            "Figures",
            "Tables",
        ],
        fill_color=CT["yellow"],
        border_color=C["yellow"],
        bullet="circle",
    )
    d.add_box(
        "scholar_box",
        "Scholar",
        subtitle="Literature management",
        content=[
            "scitex.scholar",
            "CrossRef Local Database (167M+ papers)",
            "OpenAlex Local Database (284M+ papers)",
        ],
        fill_color=CT["purple"],
        border_color=C["purple"],
        bullet="circle",
    )


def _add_output_boxes(d):
    d.add_box(
        "manuscript_box",
        "Manuscript",
        content=["Manuscript", "Supplementary materials", "Revision Letter"],
        bullet="circle",
        shape="document",
        emphasis="muted",
        height_mm=40,
    )
    d.add_box(
        "cloud_box",
        "Cloud",
        subtitle="Web Interface and collaboration",
        content=["scitex.cloud", "https://scitex.ai", "self-host"],
        bullet="circle",
        shape="stadium",
        emphasis="muted",
    )


def _add_spacers(d):
    d.add_box("spacer_box", "", fill_color="none", border_color="none")
    d.add_box("source_pad_box", "", fill_color="none", border_color="none")
    d.add_box(
        "paper_pad_box",
        "",
        fill_color="none",
        border_color="none",
        height_mm=120,
    )


def _add_containers(d, C, CT):
    d.add_container(
        "upper_row_container",
        children=["scripts_box", "linter_box", "spacer_box", "cloud_box"],
        direction="row",
        fill_color="none",
        border_color="none",
    )
    d.add_container(
        "analysis_container",
        title="Analysis & Visualization",
        title_loc="upper center",
        children=["core_box", "domain_box"],
        direction="row",
        fill_color=CT["lightblue"],
        border_color=C["lightblue"],
    )
    d.add_container(
        "main_container",
        children=[
            "analysis_container",
            "outputs_box",
            "writer_box",
            "scholar_box",
        ],
        direction="column",
    )
    d.add_container(
        "source_col_container",
        children=["source_box", "source_pad_box"],
        direction="column",
        fill_color="none",
        border_color="none",
    )
    d.add_container(
        "paper_col_container",
        children=["paper_pad_box", "manuscript_box"],
        direction="column",
        fill_color="none",
        border_color="none",
    )
    d.add_container(
        "main_row_container",
        children=[
            "source_col_container",
            "main_container",
            "paper_col_container",
        ],
        direction="row",
        fill_color="none",
        border_color="none",
    )


def _add_arrows(d, C):
    # Input flow
    d.add_arrow("scripts_box", "linter_box")
    d.add_arrow("linter_box", "core_box")
    d.add_arrow("source_box", "analysis_container", curve=-0.3)

    # Analysis flow
    d.add_arrow(
        "outputs_box",
        "writer_box",
    )
    d.add_arrow("outputs_box", "analysis_container")
    d.add_arrow("analysis_container", "outputs_box")
    d.add_arrow("scholar_box", "writer_box")

    # Output flow
    d.add_arrow(
        "writer_box",
        "manuscript_box",
    )

    # Clew Verification
    d.add_arrow(
        "manuscript_box",
        "outputs_box",
        color=C["red"],
        label="scitex.clew\nverification",
    )
    d.add_arrow(
        "outputs_box",
        "analysis_container",
        color=C["red"],
        label="scitex.clew\nverification",
        source_anchor="top-left",
        target_anchor="bottom-left",
    )
    d.add_arrow(
        "analysis_container",
        "source_box",
        curve=-0.3,
        color=C["red"],
        label="scitex.clew\nverification",
        source_anchor="left",
        target_anchor="right",
    )


@stx.session
def main(
    CONFIG=stx.session.INJECTED,
    plt=stx.session.INJECTED,
    COLORS=stx.session.INJECTED,
    rngg=stx.session.INJECTED,
    logger=stx.session.INJECTED,
):
    ALPHA = 0.1
    CT = {k: (v[0], v[1], v[2], ALPHA) for k, v in COLORS.items()}

    d = Diagram(title="SciTeX Ecosystem", gap_mm=10)

    _add_input_boxes(d, COLORS, CT)
    _add_analysis_boxes(d, COLORS, CT)
    _add_publication_boxes(d, COLORS, CT)
    _add_output_boxes(d)
    _add_spacers(d)
    _add_containers(d, COLORS, CT)
    _add_arrows(d, COLORS)

    fig, ax = d.render(auto_fix=True)
    stx.io.save(fig, CONFIG.SDIR_OUT / "workflow.png", dpi=300, watermark=True)

    return 0


if __name__ == "__main__":
    main()

# EOF
