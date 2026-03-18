#!/usr/bin/env python3
"""
Synchronous test script for PDF downloads.
Tests specific DOIs that are failing.
"""

from scitex import logging
from pathlib import Path

# Setup detailed logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def test_scholar_download(doi):
    """Test download using Scholar module."""
    from scitex.scholar import Scholar, ScholarConfig

    print(f"\n{'='*60}")
    print(f"Testing Scholar download for DOI: {doi}")
    print(f"{'='*60}\n")

    # Initialize Scholar with custom config
    config = ScholarConfig()
    config.enable_auto_download = False  # Manual download
    config.openathens_enabled = False    # Disable OpenAthens for open access test
    config.use_scihub = False            # Disable Sci-Hub for this test

    scholar = Scholar(config=config)

    # Search for the paper
    print(f"Searching for DOI: {doi}")
    papers = scholar.search(f'doi:"{doi}"', limit=1)

    if not papers:
        print("ERROR: Paper not found!")
        return

    paper = papers[0]
    print(f"\nFound paper: {paper.title}")
    print(f"DOI: {paper.doi}")
    print(f"URL: {paper.url}")
    print(f"Open Access: {paper.is_open_access}")
    print(f"Journal: {paper.journal}")
    print(f"Year: {paper.year}")

    # Try to download
    print("\nAttempting download...")
    output_dir = Path(".dev/scholar_test")
    output_dir.mkdir(exist_ok=True)

    try:
        pdf_path = scholar.download_pdf(
            paper,
            output_dir=output_dir
        )

        if pdf_path:
            print(f"✓ Downloaded to: {pdf_path}")
            print(f"  File size: {pdf_path.stat().st_size} bytes")
        else:
            print("✗ Download failed!")

            # Try to get more details
            print("\nDebug info:")
            downloader = scholar._pdf_downloader
            if downloader:
                print(f"  Downloader config:")
                print(f"    use_translators: {downloader.use_translators}")
                print(f"    use_scihub: {downloader.use_scihub}")
                print(f"    use_playwright: {downloader.use_playwright}")
                print(f"    use_openathens: {downloader.use_openathens}")

                # Check download methods used
                if hasattr(downloader, '_download_methods'):
                    print(f"  Methods tried: {downloader._download_methods.get(doi, 'None')}")

    except Exception as e:
        print(f"ERROR during download: {e}")
        import traceback
        traceback.print_exc()

def main():
    """Test multiple DOIs."""
    test_dois = [
        "10.3389/fnins.2019.00885",  # Open access Frontiers paper
        "10.1016/j.yebeh.2024.109736",  # User requested DOI
    ]

    for doi in test_dois:
        test_scholar_download(doi)
        print("\n" + "="*60 + "\n")

if __name__ == "__main__":
    main()
