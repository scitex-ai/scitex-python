#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: 2025-12-11 16:30:00
# File: /home/ywatanabe/proj/scitex-code/examples/msword/02_convert_to_tex.py

"""
Example: Convert Word documents to LaTeX.

This example demonstrates how to:
1. Load a DOCX file
2. Convert it to LaTeX using export_tex
3. Use convert_docx_to_tex for direct conversion
"""

from pathlib import Path

import scitex as stx
from scitex.msword import load_docx, convert_docx_to_tex
from scitex.tex import export_tex

# Path to sample documents
DOCS_DIR = Path(__file__).parent.parent.parent / "docs" / "MSWORD_MANUSCTIPS"
RESNA_DOCX = DOCS_DIR / "RESNA 2025 Scientific Paper Template.docx"
IOP_DOCX = DOCS_DIR / "IOP-SCIENCE-Word-template-Double-anonymous.docx"


@stx.session
def main(
    CONFIG=stx.INJECTED,
    logger=stx.INJECTED,
):
    """Convert Word documents to LaTeX format."""
    out = Path(CONFIG.SDIR_OUT)

    logger.info("=" * 60)
    logger.info("Example: Word to LaTeX Conversion")
    logger.info("=" * 60)

    # Example 1: Two-step conversion
    if RESNA_DOCX.exists():
        logger.info(f"\n1. Two-Step Conversion: {RESNA_DOCX.name}")
        doc = load_docx(RESNA_DOCX, profile="resna-2025")
        logger.info(f"   Loaded {len(doc['blocks'])} blocks")

        output_path = out / "resna_two_step.tex"
        export_tex(doc, output_path)
        logger.info(f"   Saved: {output_path}")
    else:
        logger.warning(f"File not found: {RESNA_DOCX}")

    # Example 2: Direct conversion
    if IOP_DOCX.exists():
        logger.info(f"\n2. Direct Conversion: {IOP_DOCX.name}")
        output_path = out / "iop_direct.tex"
        convert_docx_to_tex(IOP_DOCX, output_path, profile="iop-double-anonymous")
        logger.info(f"   Saved: {output_path}")
    else:
        logger.warning(f"File not found: {IOP_DOCX}")

    # Example 3: Custom LaTeX options
    if RESNA_DOCX.exists():
        logger.info("\n3. Custom LaTeX Export Options")
        doc = load_docx(RESNA_DOCX, profile="resna")
        output_path = out / "resna_custom.tex"
        export_tex(
            doc,
            output_path,
            document_class="report",
            packages=["booktabs", "siunitx", "natbib"],
            preamble=r"""
% Custom preamble
\setlength{\parindent}{0pt}
\setlength{\parskip}{1em}
""",
        )
        logger.info(f"   Saved: {output_path}")

    logger.info(f"\nAll outputs saved to: {out}")


if __name__ == "__main__":
    main()
