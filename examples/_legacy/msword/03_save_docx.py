#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: 2025-12-11 16:30:00
# File: /home/ywatanabe/proj/scitex-code/examples/msword/03_save_docx.py

"""
Example: Save/export Word documents with different profiles.

This example demonstrates how to:
1. Load a document with one profile
2. Save it with a different journal profile
3. Create a new document from scratch
"""

from pathlib import Path

import scitex as stx
from scitex.msword import load_docx, save_docx, get_profile

# Path to sample documents
DOCS_DIR = Path(__file__).parent.parent.parent / "docs" / "MSWORD_MANUSCTIPS"
RESNA_DOCX = DOCS_DIR / "RESNA 2025 Scientific Paper Template.docx"


@stx.session
def main(
    CONFIG=stx.INJECTED,
    logger=stx.INJECTED,
):
    """Save/export Word documents with different profiles."""
    out = Path(CONFIG.SDIR_OUT)

    logger.info("=" * 60)
    logger.info("Example: Save Word Documents")
    logger.info("=" * 60)

    # Example 1: Profile switching
    if RESNA_DOCX.exists():
        logger.info(f"\n1. Profile Switching: RESNA -> IEEE")
        doc = load_docx(RESNA_DOCX, profile="resna-2025")
        logger.info(f"   Loaded {len(doc['blocks'])} blocks")

        resna_profile = get_profile("resna-2025")
        ieee_profile = get_profile("ieee")
        logger.info(f"   RESNA columns: {resna_profile.columns}")
        logger.info(f"   IEEE columns: {ieee_profile.columns}")

        output_path = out / "converted_to_ieee.docx"
        save_docx(doc, output_path, profile="ieee")
        logger.info(f"   Saved: {output_path}")
    else:
        logger.warning(f"File not found: {RESNA_DOCX}")

    # Example 2: Create document from scratch
    logger.info("\n2. Create Document from Scratch")
    doc = {
        "blocks": [
            {"type": "heading", "level": 1, "text": "Introduction"},
            {"type": "paragraph", "text": "This is the introduction section."},
            {"type": "heading", "level": 1, "text": "Methods"},
            {"type": "heading", "level": 2, "text": "Participants"},
            {"type": "paragraph", "text": "We recruited 50 participants."},
            {"type": "heading", "level": 1, "text": "Results"},
            {"type": "paragraph", "text": "Results showed significant differences."},
            {
                "type": "table",
                "rows": [
                    ["Group", "Mean", "SD"],
                    ["Control", "45.2", "12.3"],
                    ["Treatment", "67.8", "15.1"],
                ],
            },
            {"type": "heading", "level": 1, "text": "Discussion"},
            {"type": "paragraph", "text": "These findings support our hypothesis."},
            {"type": "heading", "level": 1, "text": "References"},
            {
                "type": "reference-paragraph",
                "ref_number": 1,
                "ref_text": "Smith, J. (2024). Title of Paper. Journal, 10(2), 123-145.",
            },
        ],
        "metadata": {"title": "Example Manuscript", "author": "John Doe"},
        "images": [],
        "references": [
            {"number": 1, "text": "Smith, J. (2024). Title of Paper. Journal, 10(2), 123-145."},
        ],
    }

    profiles = ["generic", "mdpi-ijerph", "ieee", "springer"]
    for profile_name in profiles:
        output_path = out / f"manuscript_{profile_name}.docx"
        save_docx(doc, output_path, profile=profile_name)
        logger.info(f"   {profile_name}: {output_path.name} ({output_path.stat().st_size:,} bytes)")

    # Example 3: Formatted content
    logger.info("\n3. Create Document with Formatted Text")
    doc = {
        "blocks": [
            {"type": "heading", "level": 1, "text": "Formatted Content Example"},
            {
                "type": "paragraph",
                "text": "Mixed formatting example",
                "runs": [
                    {"text": "This paragraph contains "},
                    {"text": "bold text", "bold": True},
                    {"text": ", "},
                    {"text": "italic text", "italic": True},
                    {"text": ", and "},
                    {"text": "underlined text", "underline": True},
                    {"text": "."},
                ],
            },
        ],
        "metadata": {},
        "images": [],
        "references": [],
    }

    output_path = out / "formatted_doc.docx"
    save_docx(doc, output_path, profile="generic")
    logger.info(f"   Saved: {output_path}")

    logger.info(f"\nAll outputs saved to: {out}")


if __name__ == "__main__":
    main()
