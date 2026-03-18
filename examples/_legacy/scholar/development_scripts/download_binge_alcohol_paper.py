#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-01-25 02:08:00 (ywatanabe)"
# File: ./.dev/download_binge_alcohol_paper.py
# ----------------------------------------

"""
Download specific paper about binge alcohol drinking using OpenAthens.
"""

import os
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from scitex.scholar import Scholar


def download_alcohol_paper():
    """Download the binge alcohol paper."""

    # Enable OpenAthens
    os.environ["SCITEX_SCHOLAR_OPENATHENS_ENABLED"] = "true"
    os.environ["SCITEX_SCHOLAR_DEBUG_MODE"] = "true"

    # Check if email is set
    email = os.environ.get("SCITEX_SCHOLAR_OPENATHENS_EMAIL")
    if not email:
        print("Please set your institutional email:")
        print("export SCITEX_SCHOLAR_OPENATHENS_EMAIL='your.email@institution.edu'")
        return

    print(f"Using email: {email}")

    # Initialize Scholar
    print("\nInitializing Scholar...")
    scholar = Scholar()

    # Search for the paper
    print("\nSearching for paper...")
    query = "Suppression of binge alcohol drinking by an inhibitory neuronal ensemble in the mouse medial orbitofrontal cortex"
    # Try different search strategies
    papers = scholar.search(query, limit=5)

    if not papers:
        # Try with shorter query
        print("\nTrying shorter query...")
        papers = scholar.search("binge alcohol orbitofrontal cortex mouse", limit=10)

    if not papers:
        print("❌ No papers found")
        return

    print(f"\nFound {len(papers)} papers:")
    for i, paper in enumerate(papers, 1):
        print(f"\n{i}. {paper.title}")
        print(f"   Authors: {', '.join(paper.authors[:3])}...")
        print(f"   Year: {paper.year}")
        print(f"   Journal: {paper.journal}")
        if paper.doi:
            print(f"   DOI: {paper.doi}")

    # Find the exact match
    target_paper = None
    for paper in papers:
        if "binge alcohol" in paper.title.lower() and "orbitofrontal" in paper.title.lower():
            target_paper = paper
            break

    if not target_paper:
        # Take the first result
        target_paper = papers[0]

    print(f"\n📄 Selected paper: {target_paper.title}")

    # Create output directory
    output_dir = Path("./.dev/alcohol_paper_pdf")
    output_dir.mkdir(parents=True, exist_ok=True)

    # Download the PDF
    print("\nDownloading PDF...")
    try:
        if target_paper.doi:
            # Use DOI if available
            result = scholar.download_pdfs(
                [target_paper.doi],
                download_dir=output_dir,
                show_progress=True,
                acknowledge_ethical_usage=False
            )
        else:
            # Use the paper object
            result = scholar.download_pdfs(
                [target_paper],
                download_dir=output_dir,
                show_progress=True,
                acknowledge_ethical_usage=False
            )

        # Check if download was successful
        pdf_files = list(output_dir.glob("*.pdf"))
        if pdf_files:
            print(f"\n✅ Successfully downloaded PDF!")
            for pdf in pdf_files:
                size_mb = pdf.stat().st_size / (1024 * 1024)
                print(f"   File: {pdf.name}")
                print(f"   Size: {size_mb:.1f} MB")
                print(f"   Path: {pdf.absolute()}")
        else:
            print("\n❌ PDF download failed")
            print("   This might be because:")
            print("   - The paper is not available through your institution")
            print("   - OpenAthens authentication needs to be refreshed")
            print("   - The paper is not available as PDF")

    except Exception as e:
        print(f"\n❌ Error downloading PDF: {e}")
        import traceback
        traceback.print_exc()

    # Save paper info
    print("\nSaving paper information...")
    info_file = output_dir / "paper_info.txt"
    with open(info_file, "w") as f:
        f.write(f"Title: {target_paper.title}\n")
        f.write(f"Authors: {', '.join(target_paper.authors)}\n")
        f.write(f"Year: {target_paper.year}\n")
        f.write(f"Journal: {target_paper.journal}\n")
        if target_paper.doi:
            f.write(f"DOI: {target_paper.doi}\n")
        f.write(f"\nAbstract:\n{target_paper.abstract}\n")

    print(f"   Info saved to: {info_file}")


if __name__ == "__main__":
    download_alcohol_paper()
