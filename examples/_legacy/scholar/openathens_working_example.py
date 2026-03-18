#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-01-25 02:05:00 (ywatanabe)"
# File: ./examples/scholar/openathens_working_example.py
# ----------------------------------------

"""
Working example of using Scholar with OpenAthens authentication.

Prerequisites:
1. Set your email: export SCITEX_SCHOLAR_OPENATHENS_EMAIL='your.email@institution.edu'
2. Enable OpenAthens: export SCITEX_SCHOLAR_OPENATHENS_ENABLED=true
"""

import os
from pathlib import Path
from scitex.scholar import Scholar

def main():
    """Example of using OpenAthens with Scholar."""

    # Check if email is set
    email = os.environ.get("SCITEX_SCHOLAR_OPENATHENS_EMAIL")
    if not email:
        print("Please set your institutional email:")
        print("export SCITEX_SCHOLAR_OPENATHENS_EMAIL='your.email@institution.edu'")
        return

    print(f"Using institutional email: {email}")

    # Enable OpenAthens
    os.environ["SCITEX_SCHOLAR_OPENATHENS_ENABLED"] = "true"

    # Initialize Scholar (OpenAthens will be configured automatically)
    scholar = Scholar()

    # Search for papers
    print("\nSearching for papers...")
    papers = scholar.search("deep learning neuroscience", limit=5)
    print(f"Found {len(papers)} papers")

    # Show paper titles
    print("\nPapers found:")
    for i, paper in enumerate(papers, 1):
        print(f"{i}. {paper.title}")
        if paper.doi:
            print(f"   DOI: {paper.doi}")

    # Download PDFs using OpenAthens
    print("\n" + "="*60)
    print("Downloading PDFs with OpenAthens authentication")
    print("="*60)

    # Create output directory
    output_dir = Path("./openathens_pdfs")
    output_dir.mkdir(exist_ok=True)

    # Download PDFs - OpenAthens will authenticate automatically if needed
    results = scholar.download_pdfs(
        papers,
        download_dir=output_dir,
        show_progress=True,
        acknowledge_ethical_usage=False  # We're using OpenAthens, not Sci-Hub
    )

    # Show results
    print(f"\n✅ Downloaded {len(results)} PDFs")
    print(f"📁 Files saved to: {output_dir.absolute()}")

    # List downloaded files
    pdf_files = list(output_dir.glob("*.pdf"))
    if pdf_files:
        print("\nDownloaded files:")
        for pdf in pdf_files:
            size_mb = pdf.stat().st_size / (1024 * 1024)
            print(f"  - {pdf.name} ({size_mb:.1f} MB)")

    # Save bibliography
    print("\nSaving bibliography...")
    papers.save(output_dir / "bibliography.bib")
    print(f"📚 Bibliography saved to: {output_dir / 'bibliography.bib'}")


if __name__ == "__main__":
    main()
