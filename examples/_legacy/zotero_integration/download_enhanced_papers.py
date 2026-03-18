#!/usr/bin/env python3
"""Download PDFs for enhanced papers using Zotero Connector."""

import asyncio
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from scitex.scholar import Scholar
from scitex.io import load


async def download_with_zotero(dois, headless=False):
    """Download PDFs using Zotero Connector."""
    try:
        from playwright.async_api import async_playwright
    except ImportError:
        print("Please install playwright: pip install playwright")
        print("Then run: playwright install chromium")
        return

    print(f"\nDownloading {len(dois)} papers via Zotero Connector...")
    print("Make sure:")
    print("  • Chrome is open with Zotero Connector installed")
    print("  • You're logged into your UniMelb account")
    print("  • Zotero desktop is running")
    print("-" * 60)

    async with async_playwright() as p:
        # Launch browser
        # For headless=False, it will open a visible browser window
        browser = await p.chromium.launch(headless=headless)
        page = await browser.new_page()

        success_count = 0

        for i, doi in enumerate(dois):
            print(f"\n[{i+1}/{len(dois)}] Processing: {doi}")

            try:
                # Navigate to DOI page
                await page.goto(f"https://doi.org/{doi}")

                # Wait for page to load
                await asyncio.sleep(2)

                # Trigger Zotero Connector save (Ctrl+Shift+S)
                await page.keyboard.press('Control+Shift+s')

                # Wait for Zotero to process
                await asyncio.sleep(3)

                print(f"  ✓ Triggered save for: {doi}")
                success_count += 1

            except Exception as e:
                print(f"  ✗ Error: {e}")

        await browser.close()

    print(f"\n{'='*60}")
    print(f"Completed: {success_count}/{len(dois)} papers")
    print("Check your Zotero library for the downloaded PDFs!")
    print(f"{'='*60}")


async def main():
    """Main workflow: Enhance BibTeX and download PDFs."""

    # Step 1: Enhance your BibTeX file to get DOIs
    print("Step 1: Enhancing BibTeX file to find DOIs...")
    print("=" * 60)

    scholar = Scholar(
        email_crossref="research@example.com",
        email_pubmed="research@example.com"
    )

    input_path = "/home/ywatanabe/win/downloads/papers.bib"
    enhanced_path = "/home/ywatanabe/win/downloads/papers_with_dois.bib"

    # Enhance to get DOIs
    enhanced = scholar.enrich_bibtex(
        input_path,
        output_path=enhanced_path,
        add_missing_abstracts=True
    )

    # Get papers with DOIs
    papers_with_dois = [p for p in enhanced if p.doi]
    print(f"\nFound {len(papers_with_dois)} papers with DOIs")

    # Show first few
    print("\nSample papers ready for download:")
    for i, paper in enumerate(papers_with_dois[:5]):
        print(f"{i+1}. {paper.title[:60]}...")
        print(f"   DOI: {paper.doi}")

    # Step 2: Download PDFs via Zotero
    print(f"\n{'='*60}")
    print("Step 2: Download PDFs via Zotero Connector")
    print("=" * 60)

    # Get DOIs to download (first 10 as example)
    dois_to_download = [p.doi for p in papers_with_dois[:10]]

    # Ask for confirmation
    response = input(f"\nDownload {len(dois_to_download)} PDFs to Zotero? (y/n): ")

    if response.lower() == 'y':
        await download_with_zotero(dois_to_download, headless=False)
    else:
        print("Skipping download.")
        print("\nTo download manually:")
        print("1. Open each DOI URL in Chrome")
        print("2. Press Ctrl+Shift+S to save to Zotero")
        print("\nOr use this list of URLs:")
        for doi in dois_to_download[:5]:
            print(f"  https://doi.org/{doi}")


if __name__ == "__main__":
    # Run the async main function
    asyncio.run(main())
