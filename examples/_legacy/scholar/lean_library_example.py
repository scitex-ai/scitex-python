#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-01-25 03:45:00 (ywatanabe)"
# File: ./examples/scholar/lean_library_example.py
# ----------------------------------------

"""
Example demonstrating Lean Library integration in SciTeX Scholar.

This example shows how to use Lean Library browser extension for
institutional PDF access. Lean Library provides automatic authentication
without manual login after initial setup.

Prerequisites:
1. Install Lean Library browser extension from Chrome/Firefox store
2. Configure it with your institution
3. Ensure you're logged in to your institution
"""

import asyncio
from pathlib import Path
from scitex.scholar import Scholar, ScholarConfig


async def main():
    """Main example demonstrating Lean Library functionality."""

    print("=== SciTeX Scholar with Lean Library Example ===\n")

    # Configure Scholar with Lean Library enabled (it's enabled by default)
    config = ScholarConfig(
        use_lean_library=True,  # This is the default
        enable_auto_enrich=True,  # Enrich with impact factors
        pdf_dir="./scholar_pdfs",  # Where to save PDFs
    )

    # Create Scholar instance
    scholar = Scholar(config)

    print("Configuration:")
    print(f"  Lean Library enabled: {config.use_lean_library}")
    print(f"  OpenAthens enabled: {config.openathens_enabled}")
    print(f"  PDF directory: {config.pdf_dir}\n")

    # Example 1: Search for papers
    print("1. Searching for recent Nature papers on climate change...")
    papers = await scholar.search_async(
        query="climate change",
        sources=["pubmed"],
        year_min=2023,
        limit=5
    )

    print(f"Found {len(papers)} papers\n")

    # Show papers
    for i, paper in enumerate(papers[:3], 1):
        print(f"{i}. {paper.title}")
        print(f"   Authors: {paper.first_author} et al.")
        print(f"   Journal: {paper.journal}")
        print(f"   DOI: {paper.doi}")
        print(f"   Impact Factor: {paper.impact_factor}")
        print()

    # Example 2: Download PDFs using Lean Library
    print("\n2. Downloading PDFs with Lean Library...")
    print("   (Lean Library will be tried first for institutional access)\n")

    # Filter for high-impact papers
    high_impact_papers = papers.filter(impact_factor_min=10.0)

    if high_impact_papers:
        # Download PDFs
        downloaded = await scholar.download_pdfs_async(
            high_impact_papers,
            show_progress=True
        )

        print(f"\nDownloaded {len(downloaded)} PDFs:")
        for paper in downloaded:
            if paper.pdf_path and paper.pdf_path.exists():
                size_kb = paper.pdf_path.stat().st_size / 1024
                print(f"  ✓ {paper.doi}")
                print(f"    File: {paper.pdf_path.name} ({size_kb:.1f} KB)")
                print(f"    Method: {paper.pdf_source}")
    else:
        print("No high-impact papers found to download")

    # Example 3: Test specific paywalled papers
    print("\n\n3. Testing Lean Library with specific paywalled papers...")

    # These are likely paywalled papers from major publishers
    test_dois = [
        "10.1038/s41586-023-06083-8",  # Nature
        "10.1126/science.adi7899",      # Science
        "10.1016/j.cell.2023.12.012",   # Cell
    ]

    print("Downloading specific papers:")
    for doi in test_dois:
        print(f"  - {doi}")

    # Download with detailed results
    results = await scholar.pdf_downloader.batch_download_async(
        test_dois,
        output_dir=Path(config.pdf_dir) / "test_downloads",
        show_progress=True,
        return_detailed=True  # Get download methods
    )

    print("\n\nDownload Results:")
    print("-" * 60)

    for doi, result in results.items():
        if result:
            print(f"✓ {doi}")
            print(f"  Path: {result['path'].name}")
            print(f"  Method: {result['method']}")
            if result['method'] == "Lean Library":
                print("  → Successfully used Lean Library for institutional access!")
        else:
            print(f"✗ {doi} - Failed to download")

    # Summary
    lean_library_count = sum(
        1 for r in results.values()
        if r and r.get('method') == 'Lean Library'
    )

    print(f"\n\nSummary:")
    print(f"  Total attempts: {len(results)}")
    print(f"  Successful downloads: {sum(1 for r in results.values() if r)}")
    print(f"  Via Lean Library: {lean_library_count}")

    if lean_library_count > 0:
        print("\n✅ Lean Library is working! Your institutional access is being used.")
    else:
        print("\n⚠️  Lean Library was not used. Possible reasons:")
        print("   1. Extension not installed or not configured")
        print("   2. Not logged in to your institution")
        print("   3. Papers were available via open access")
        print("   4. Your institution doesn't have subscriptions to these journals")


if __name__ == "__main__":
    print("Lean Library Example for SciTeX Scholar\n")
    print("Prerequisites:")
    print("1. Install Lean Library extension from browser store")
    print("2. Configure with your institution")
    print("3. Ensure you're logged in\n")

    # Run the example
    asyncio.run(main())
