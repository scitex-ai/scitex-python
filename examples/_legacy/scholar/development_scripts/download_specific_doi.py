#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-01-25 02:10:00 (ywatanabe)"
# File: ./.dev/download_specific_doi.py
# ----------------------------------------

"""
Download a specific paper by DOI using OpenAthens.
First, let's search for the paper to find its DOI.
"""

import os
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from scitex.scholar import Scholar, Paper


def download_paper():
    """Search and download the binge alcohol paper."""

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

    # Create output directory
    output_dir = Path("./.dev/alcohol_paper_pdf")
    output_dir.mkdir(parents=True, exist_ok=True)

    # This paper seems to be:
    # "Suppression of binge alcohol drinking by BNST CRF neurons"
    # Let's try some known DOIs for alcohol/orbitofrontal cortex papers

    print("\nTrying known alcohol/brain research DOIs...")

    # Some potential DOIs (you might need to find the exact one)
    test_dois = [
        "10.1038/s41386-021-01055-w",  # Nature Neuropsychopharmacology
        "10.1016/j.biopsych.2021.02.970",  # Biological Psychiatry
        "10.1038/s41593-021-00897-3",  # Nature Neuroscience
    ]

    for doi in test_dois:
        print(f"\n📄 Trying DOI: {doi}")

        try:
            # Download the PDF
            result = scholar.download_pdfs(
                [doi],
                download_dir=output_dir,
                show_progress=True,
                acknowledge_ethical_usage=False
            )

            # Check if successful
            pdf_files = list(output_dir.glob("*.pdf"))
            if pdf_files:
                for pdf in pdf_files:
                    if doi.replace("/", "_") in pdf.name or doi.split("/")[-1] in pdf.name:
                        size_mb = pdf.stat().st_size / (1024 * 1024)
                        print(f"✅ Successfully downloaded!")
                        print(f"   File: {pdf.name}")
                        print(f"   Size: {size_mb:.1f} MB")
                        print(f"   Path: {pdf.absolute()}")

                        # Try to get paper info
                        try:
                            # Search for the DOI to get metadata
                            papers = scholar.search(doi, limit=1)
                            if papers:
                                paper = papers[0]
                                print(f"\n📖 Paper Info:")
                                print(f"   Title: {paper.title}")
                                print(f"   Authors: {', '.join(paper.authors[:3])}...")
                                print(f"   Journal: {paper.journal}")
                                print(f"   Year: {paper.year}")
                        except:
                            pass

        except Exception as e:
            print(f"   ❌ Failed: {str(e)[:100]}")

    # If you have the exact DOI, you can use it directly:
    print("\n\nIf you have the exact DOI for the paper:")
    print("'Suppression of binge alcohol drinking by an inhibitory neuronal ensemble'")
    print("You can modify this script to use it directly.")

    # Alternative: Create a Paper object manually if you know the details
    print("\n\nAlternatively, downloading with manual Paper object...")

    # Create Paper object with known details
    manual_paper = Paper(
        title="Suppression of binge alcohol drinking by an inhibitory neuronal ensemble in the mouse medial orbitofrontal cortex",
        authors=["Author1", "Author2"],  # Replace with actual authors
        abstract="Research on binge alcohol drinking and orbitofrontal cortex",
        source="manual",
        year=2021,  # Replace with actual year
        journal="Nature Neuroscience"  # Replace with actual journal
    )

    # If you know the DOI, add it
    # manual_paper.doi = "10.xxxx/xxxxx"

    print(f"\nCreated manual paper: {manual_paper.title}")

    # List all downloaded PDFs
    print("\n\n📁 All downloaded PDFs:")
    all_pdfs = list(output_dir.glob("*.pdf"))
    if all_pdfs:
        for pdf in all_pdfs:
            size_mb = pdf.stat().st_size / (1024 * 1024)
            print(f"  - {pdf.name} ({size_mb:.1f} MB)")
    else:
        print("  No PDFs downloaded yet")


if __name__ == "__main__":
    download_paper()
