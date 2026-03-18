#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: 2025-12-11 16:30:00
# File: /home/ywatanabe/proj/scitex-code/examples/msword/05_extract_content.py

"""
Example: Extract specific content from Word documents.

This example demonstrates how to:
1. Extract images from a document
2. Extract and parse references
3. Extract figure/table captions
4. Extract section structure
"""

from pathlib import Path
import json

import scitex as stx
from scitex.msword import load_docx

# Path to sample documents
DOCS_DIR = Path(__file__).parent.parent.parent / "docs" / "MSWORD_MANUSCTIPS"
RESNA_DOCX = DOCS_DIR / "RESNA 2025 Scientific Paper Template.docx"
IOP_DOCX = DOCS_DIR / "IOP-SCIENCE-Word-template-Double-anonymous.docx"


@stx.session
def main(
    CONFIG=stx.INJECTED,
    logger=stx.INJECTED,
):
    """Extract specific content from Word documents."""
    out = Path(CONFIG.SDIR_OUT)

    logger.info("=" * 60)
    logger.info("Example: Extract Content from Word Documents")
    logger.info("=" * 60)

    if not RESNA_DOCX.exists():
        logger.error(f"File not found: {RESNA_DOCX}")
        return

    # Load document
    doc = load_docx(RESNA_DOCX, profile="resna", extract_images=True)

    # Example 1: Extract images
    logger.info(f"\n1. Extract Images")
    images = doc["images"]
    logger.info(f"   Found {len(images)} images")

    if images:
        images_dir = out / "extracted_images"
        images_dir.mkdir(exist_ok=True)

        for i, img in enumerate(images):
            ext = img.get("extension", ".png")
            filename = images_dir / f"image_{i + 1}{ext}"
            if "data" in img:
                filename.write_bytes(img["data"])
                logger.info(f"   Saved: {filename.name} ({img.get('size_bytes', 0):,} bytes)")

    # Example 2: Extract references
    logger.info(f"\n2. Extract References")
    references = doc["references"]
    logger.info(f"   Found {len(references)} references")

    if references:
        refs_file = out / "references.txt"
        with refs_file.open("w") as f:
            for ref in references:
                num = ref.get("number", "?")
                text = ref.get("text", "")
                f.write(f"[{num}] {text}\n\n")
        logger.info(f"   Saved: {refs_file}")

    # Example 3: Extract captions
    logger.info(f"\n3. Extract Captions")
    captions = [b for b in doc["blocks"] if b.get("type") == "caption"]
    figure_captions = [c for c in captions if c.get("caption_type") == "figure"]
    table_captions = [c for c in captions if c.get("caption_type") == "table"]

    logger.info(f"   Figure captions: {len(figure_captions)}")
    logger.info(f"   Table captions: {len(table_captions)}")

    # Example 4: Extract structure
    logger.info(f"\n4. Document Structure")
    headings = [b for b in doc["blocks"] if b.get("type") == "heading"]
    logger.info(f"   Sections: {len(headings)}")
    for h in headings:
        level = h.get("level", 1)
        text = h.get("text", "")
        indent = "  " * (level - 1)
        logger.info(f"   {indent}[H{level}] {text}")

    # Example 5: Export to JSON
    logger.info(f"\n5. Export to JSON")
    doc_clean = {
        "metadata": doc["metadata"],
        "blocks": doc["blocks"],
        "references": doc["references"],
        "warnings": doc["warnings"],
        "statistics": {
            "total_blocks": len(doc["blocks"]),
            "headings": len(headings),
            "paragraphs": len([b for b in doc["blocks"] if b.get("type") == "paragraph"]),
            "tables": len([b for b in doc["blocks"] if b.get("type") == "table"]),
            "captions": len(captions),
            "references": len(references),
        },
    }

    json_path = out / "document_structure.json"
    json_path.write_text(json.dumps(doc_clean, indent=2, default=str))
    logger.info(f"   Saved: {json_path}")

    logger.info(f"\nAll outputs saved to: {out}")


if __name__ == "__main__":
    main()
