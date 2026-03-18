#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: 2025-12-11 16:30:00
# File: /home/ywatanabe/proj/scitex-code/examples/msword/01_load_docx.py

"""
Example: Load a Word document and inspect its structure.

This example demonstrates how to:
1. Load a DOCX file using scitex.msword
2. Inspect the document structure (blocks, metadata, images, references)
3. Use different journal profiles
"""

from pathlib import Path
from scitex.msword import load_docx, list_profiles

# Path to sample documents
DOCS_DIR = Path(__file__).parent.parent.parent / "docs" / "MSWORD_MANUSCTIPS"
IOP_DOCX = DOCS_DIR / "IOP-SCIENCE-Word-template-Double-anonymous.docx"
RESNA_DOCX = DOCS_DIR / "RESNA 2025 Scientific Paper Template.docx"


def main():
    # List available profiles
    print("=" * 60)
    print("Available Journal Profiles:")
    print("=" * 60)
    for profile in list_profiles():
        print(f"  - {profile}")
    print()

    # Load IOP document
    print("=" * 60)
    print("Loading IOP Document (Double-Anonymous Template)")
    print("=" * 60)

    if IOP_DOCX.exists():
        doc = load_docx(IOP_DOCX, profile="iop-double-anonymous")

        print(f"\nMetadata:")
        for key, value in doc["metadata"].items():
            print(f"  {key}: {value}")

        print(f"\nDocument Statistics:")
        print(f"  Total blocks: {len(doc['blocks'])}")
        print(f"  Images extracted: {len(doc['images'])}")
        print(f"  References found: {len(doc['references'])}")

        # Count block types
        block_types = {}
        for block in doc["blocks"]:
            btype = block.get("type", "unknown")
            block_types[btype] = block_types.get(btype, 0) + 1

        print(f"\nBlock Types:")
        for btype, count in sorted(block_types.items()):
            print(f"  {btype}: {count}")

        print(f"\nFirst 5 blocks:")
        for i, block in enumerate(doc["blocks"][:5]):
            text = block.get("text", "")[:50]
            print(f"  [{i}] {block.get('type')}: {text}...")
    else:
        print(f"  File not found: {IOP_DOCX}")

    print()

    # Load RESNA document
    print("=" * 60)
    print("Loading RESNA 2025 Document")
    print("=" * 60)

    if RESNA_DOCX.exists():
        doc = load_docx(RESNA_DOCX, profile="resna-2025")

        print(f"\nMetadata:")
        for key, value in doc["metadata"].items():
            print(f"  {key}: {value}")

        print(f"\nDocument Statistics:")
        print(f"  Total blocks: {len(doc['blocks'])}")
        print(f"  Images extracted: {len(doc['images'])}")
        print(f"  References found: {len(doc['references'])}")

        # Count block types
        block_types = {}
        for block in doc["blocks"]:
            btype = block.get("type", "unknown")
            block_types[btype] = block_types.get(btype, 0) + 1

        print(f"\nBlock Types:")
        for btype, count in sorted(block_types.items()):
            print(f"  {btype}: {count}")

        # Show headings
        headings = [b for b in doc["blocks"] if b.get("type") == "heading"]
        if headings:
            print(f"\nSection Headings:")
            for h in headings[:10]:
                level = h.get("level", "?")
                text = h.get("text", "")[:40]
                print(f"  [H{level}] {text}")
    else:
        print(f"  File not found: {RESNA_DOCX}")


if __name__ == "__main__":
    main()
