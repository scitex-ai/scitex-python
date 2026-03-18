#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: 2025-12-11 16:30:00
# File: /home/ywatanabe/proj/scitex-code/examples/msword/06_full_pipeline.py

"""
Example: Full pipeline from Word to LaTeX with figures.

This example demonstrates the complete workflow using convert_docx_to_tex(),
which handles everything in one call:
1. Load Word document with image extraction
2. Normalize section headings
3. Link figure captions to images
4. Validate document structure
5. Export to LaTeX with figures
"""

from pathlib import Path

import scitex as stx
from scitex.msword import convert_docx_to_tex

# Path to sample documents
DOCS_DIR = Path(__file__).parent.parent.parent / "docs" / "MSWORD_MANUSCTIPS"
RESNA_DOCX = DOCS_DIR / "RESNA 2025 Scientific Paper Template.docx"
IOP_DOCX = DOCS_DIR / "IOP-SCIENCE-Word-template-Double-anonymous.docx"


@stx.session
def main(
    CONFIG=stx.INJECTED,
    logger=stx.INJECTED,
):
    """Full pipeline: Word to LaTeX with figures."""
    out = Path(CONFIG.SDIR_OUT)

    logger.info("=" * 60)
    logger.info("Full Pipeline: Word -> LaTeX (One-Liner)")
    logger.info("=" * 60)

    # Example 1: One-liner conversion with all features
    if RESNA_DOCX.exists():
        logger.info(f"\n1. Converting: {RESNA_DOCX.name}")
        logger.info("   Using convert_docx_to_tex() with all options enabled:")
        logger.info("   - link_images=True (auto-link captions to figures)")
        logger.info("   - normalize_headings=True (standardize section names)")
        logger.info("   - validate=True (check document structure)")

        output_tex = out / "resna_full_pipeline.tex"
        figures_dir = out / "resna_figures"

        convert_docx_to_tex(
            RESNA_DOCX,
            output_tex,
            profile="resna-2025",
            image_dir=figures_dir,
            link_images=True,
            link_mode="by-number",
            normalize_headings=True,
            validate=True,
        )

        logger.info(f"\n2. Output files:")
        logger.info(f"   {output_tex.name} ({output_tex.stat().st_size:,} bytes)")
        if figures_dir.exists():
            for f in sorted(figures_dir.glob("*")):
                logger.info(f"   {figures_dir.name}/{f.name} ({f.stat().st_size:,} bytes)")
    else:
        logger.warning(f"File not found: {RESNA_DOCX}")

    # Example 2: Batch conversion - minimal call
    logger.info("\n" + "=" * 60)
    logger.info("Batch Conversion (Minimal API)")
    logger.info("=" * 60)

    documents = [
        (IOP_DOCX, "iop"),
        (RESNA_DOCX, "resna"),
    ]

    for docx_path, profile in documents:
        if not docx_path.exists():
            logger.warning(f"Skipping: {docx_path.name}")
            continue

        logger.info(f"\n Processing: {docx_path.name}")

        stem = docx_path.stem.replace(" ", "_")
        output_tex = out / f"{stem}.tex"
        figures_dir = out / f"{stem}_figures"

        # Minimal call - defaults handle everything
        convert_docx_to_tex(
            docx_path,
            output_tex,
            profile=profile,
            image_dir=figures_dir,
        )

        logger.info(f"   Output: {output_tex}")
        logger.info(f"   Size: {output_tex.stat().st_size:,} bytes")

    # Example 3: Customized options
    logger.info("\n" + "=" * 60)
    logger.info("Custom Options")
    logger.info("=" * 60)

    if RESNA_DOCX.exists():
        output_tex = out / "resna_no_validation.tex"

        logger.info("\n Converting with validation disabled:")
        convert_docx_to_tex(
            RESNA_DOCX,
            output_tex,
            profile="resna",
            validate=False,  # Skip structure validation
            normalize_headings=False,  # Keep original heading text
        )
        logger.info(f"   Output: {output_tex}")

    logger.info(f"\nAll outputs saved to: {out}")


if __name__ == "__main__":
    main()
