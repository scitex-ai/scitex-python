#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: 2025-12-11 17:30:00
# File: /home/ywatanabe/proj/scitex-code/examples/msword/07_docx_to_pdf.py

"""
Example: Full pipeline from Word to PDF via structured data.

This example demonstrates the complete workflow:
1. Load Word document (.docx) -> SciTeX structured data (dict)
2. Inspect/manipulate the structured data
3. Export to LaTeX (.tex)
4. Compile to PDF

The intermediate structured data format enables:
- Programmatic manipulation of document content
- Format conversion (Word <-> LaTeX)
- Content extraction and analysis
- Template-based document generation
"""

from pathlib import Path

import scitex as stx
from scitex.msword import load_docx, list_profiles
from scitex.tex import export_tex, compile_tex

# Path to sample documents
DOCS_DIR = Path(__file__).parent.parent.parent / "docs" / "MSWORD_MANUSCTIPS"
RESNA_DOCX = DOCS_DIR / "RESNA 2025 Scientific Paper Template.docx"


@stx.session
def main(
    CONFIG=stx.INJECTED,
    logger=stx.INJECTED,
):
    """Full pipeline: Word -> Structured Data -> LaTeX -> PDF."""
    out = Path(CONFIG.SDIR_OUT)

    logger.info("=" * 60)
    logger.info("Full Pipeline: Word -> Structured Data -> PDF")
    logger.info("=" * 60)

    if not RESNA_DOCX.exists():
        logger.error(f"File not found: {RESNA_DOCX}")
        return

    # =========================================================================
    # Step 1: Load Word document to structured data
    # =========================================================================
    logger.info("\n1. Loading Word document to structured data...")

    doc = load_docx(
        RESNA_DOCX,
        profile="resna-2025",
        extract_images=True,
    )

    logger.info(f"   Loaded document with {len(doc.get('blocks', []))} blocks")

    # =========================================================================
    # Step 2: Inspect structured data
    # =========================================================================
    logger.info("\n2. Inspecting structured data...")

    # The structured data is a dict with these keys:
    logger.info(f"   Document keys: {list(doc.keys())}")

    # Count block types
    block_types = {}
    for block in doc.get("blocks", []):
        btype = block.get("type", "unknown")
        block_types[btype] = block_types.get(btype, 0) + 1

    logger.info("   Block types:")
    for btype, count in sorted(block_types.items()):
        logger.info(f"     {btype}: {count}")

    # Show metadata
    metadata = doc.get("metadata", {})
    if metadata:
        logger.info(f"   Title: {metadata.get('title', 'N/A')}")
        logger.info(f"   Author: {metadata.get('author', 'N/A')}")

    # Show image count
    images = doc.get("images", [])
    logger.info(f"   Images extracted: {len(images)}")

    # =========================================================================
    # Step 3: Manipulate structured data (optional)
    # =========================================================================
    logger.info("\n3. Manipulating structured data...")

    # Example: Add a custom metadata field
    doc["metadata"]["processed_by"] = "SciTeX MS Word Pipeline"
    from datetime import datetime
    doc["metadata"]["export_date"] = datetime.now().isoformat()

    # Example: Count words in paragraphs
    word_count = 0
    for block in doc.get("blocks", []):
        if block.get("type") == "paragraph":
            text = block.get("text", "")
            word_count += len(text.split())

    logger.info(f"   Total words in paragraphs: {word_count}")

    # =========================================================================
    # Step 4: Export to LaTeX
    # =========================================================================
    logger.info("\n4. Exporting to LaTeX...")

    tex_path = out / "resna_pipeline.tex"
    figures_dir = out / "resna_pipeline_figures"

    export_tex(
        doc,
        tex_path,
        image_dir=figures_dir,
        export_images=True,
    )

    logger.info(f"   LaTeX file: {tex_path}")
    logger.info(f"   Size: {tex_path.stat().st_size:,} bytes")

    if figures_dir.exists():
        figure_count = len(list(figures_dir.glob("*")))
        logger.info(f"   Figures directory: {figures_dir} ({figure_count} files)")

    # =========================================================================
    # Step 5: Compile to PDF
    # =========================================================================
    logger.info("\n5. Compiling LaTeX to PDF...")

    result = compile_tex(
        tex_path,
        output_dir=out,
        compiler="pdflatex",
        runs=2,
        clean=True,
    )

    if result.success:
        logger.info(f"   SUCCESS: PDF created at {result.pdf_path}")
        logger.info(f"   PDF size: {result.pdf_path.stat().st_size:,} bytes")
    else:
        logger.warning(f"   Compilation failed (exit code {result.exit_code})")
        if result.errors:
            logger.warning(f"   Errors: {len(result.errors)}")
            for err in result.errors[:3]:
                logger.warning(f"     - {err[:80]}...")
        logger.info("   NOTE: pdflatex must be installed (texlive/miktex)")

    # =========================================================================
    # Summary
    # =========================================================================
    logger.info("\n" + "=" * 60)
    logger.info("Pipeline Summary")
    logger.info("=" * 60)
    logger.info(f"Input:  {RESNA_DOCX.name}")
    logger.info(f"Output: {tex_path.name}")
    if result.success:
        logger.info(f"PDF:    {result.pdf_path.name}")
    logger.info(f"\nStructured data format enables:")
    logger.info("  - Content inspection and manipulation")
    logger.info("  - Format conversion (Word <-> LaTeX)")
    logger.info("  - Programmatic document generation")
    logger.info("  - Multi-format export from single source")


if __name__ == "__main__":
    main()
