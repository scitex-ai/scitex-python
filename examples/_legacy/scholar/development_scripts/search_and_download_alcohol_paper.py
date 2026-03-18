#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-01-25 02:11:00 (ywatanabe)"
# File: ./.dev/search_and_download_alcohol_paper.py
# ----------------------------------------

"""
Search multiple databases and download the specific alcohol paper.
"""

import os
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from scitex.scholar import Scholar


def search_and_download():
    """Search for and download the specific paper."""

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

    # The exact title
    title = "Suppression of binge alcohol drinking by an inhibitory neuronal ensemble in the mouse medial orbitofrontal cortex"

    # Try different search strategies
    print(f"\n🔍 Searching for: {title}")

    # Strategy 1: Search each database individually
    sources = ["pubmed", "semantic_scholar", "crossref", "google_scholar"]
    all_papers = []

    for source in sources:
        print(f"\n📚 Searching {source}...")
        try:
            # Try exact title first
            papers = scholar.search(f'"{title}"', limit=5, sources=[source])

            if not papers:
                # Try key terms
                papers = scholar.search("binge alcohol inhibitory orbitofrontal cortex mouse",
                                      limit=10, sources=[source])

            if papers:
                print(f"  Found {len(papers)} papers in {source}")
                for paper in papers:
                    # Check if title matches
                    if "binge alcohol" in paper.title.lower() and "orbitofrontal" in paper.title.lower():
                        print(f"  ✓ Potential match: {paper.title[:80]}...")
                        if paper.doi:
                            print(f"    DOI: {paper.doi}")
                        all_papers.append(paper)
            else:
                print(f"  No results from {source}")

        except Exception as e:
            print(f"  Error searching {source}: {str(e)[:100]}")

    # Find exact match or best match
    target_paper = None

    # First, look for exact title match
    for paper in all_papers:
        if paper.title.lower() == title.lower():
            target_paper = paper
            print(f"\n✅ Found exact match!")
            break

    # If no exact match, look for close match
    if not target_paper:
        for paper in all_papers:
            title_lower = paper.title.lower()
            if ("suppression" in title_lower and
                "binge alcohol" in title_lower and
                "inhibitory" in title_lower and
                "orbitofrontal cortex" in title_lower):
                target_paper = paper
                print(f"\n✅ Found close match!")
                break

    # If still no match, take the most relevant one
    if not target_paper and all_papers:
        target_paper = all_papers[0]
        print(f"\n⚠️  Using best available match")

    if not target_paper:
        print("\n❌ Could not find the paper in any database")
        print("\nYou may need to:")
        print("1. Check if the title is exactly correct")
        print("2. Try searching on the journal's website directly")
        print("3. Use the DOI if you have it")
        return

    # Display paper info
    print(f"\n📄 Paper found:")
    print(f"Title: {target_paper.title}")
    print(f"Authors: {', '.join(target_paper.authors[:3])}...")
    print(f"Year: {target_paper.year}")
    print(f"Journal: {target_paper.journal}")
    if target_paper.doi:
        print(f"DOI: {target_paper.doi}")

    # Create output directory
    output_dir = Path("./.dev/alcohol_paper_pdf")
    output_dir.mkdir(parents=True, exist_ok=True)

    # Download the PDF
    print("\n📥 Downloading PDF...")

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
            # Use paper object
            result = scholar.download_pdfs(
                [target_paper],
                download_dir=output_dir,
                show_progress=True,
                acknowledge_ethical_usage=False
            )

        # Check results
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

            if target_paper.doi:
                print(f"\n💡 Try accessing directly: https://doi.org/{target_paper.doi}")

    except Exception as e:
        print(f"\n❌ Error downloading: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    search_and_download()
