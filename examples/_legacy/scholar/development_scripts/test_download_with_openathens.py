#!/usr/bin/env python3
"""
Test PDF downloads with OpenAthens authentication.
"""

from scitex import logging
from pathlib import Path

# Setup detailed logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def test_scholar_download_with_openathens(doi):
    """Test download using Scholar module with OpenAthens."""
    from scitex.scholar import Scholar, ScholarConfig

    print(f"\n{'='*60}")
    print(f"Testing Scholar download with OpenAthens for DOI: {doi}")
    print(f"{'='*60}\n")

    # Initialize Scholar with OpenAthens enabled
    config = ScholarConfig()
    config.enable_auto_download = False  # Manual download
    config.openathens_enabled = True     # Enable OpenAthens
    config.use_scihub = False           # Disable Sci-Hub for this test

    scholar = Scholar(config=config)

    # Search for the paper using CrossRef (better for DOI search)
    print(f"Searching for DOI: {doi}")
    papers = scholar.search(f'{doi}', sources=['crossref'], limit=1)

    if not papers:
        # Try with semantic_scholar
        print("Not found in CrossRef, trying Semantic Scholar...")
        papers = scholar.search(f'{doi}', sources=['semantic_scholar'], limit=1)

    if not papers:
        print("ERROR: Paper not found in any source!")
        return

    paper = papers[0]
    print(f"\nFound paper: {paper.title}")
    print(f"DOI: {paper.doi}")
    print(f"URL: {paper.url}")
    print(f"Open Access: {paper.is_open_access}")
    print(f"Journal: {paper.journal}")
    print(f"Year: {paper.year}")

    # Try to download
    print("\nAttempting download with OpenAthens...")
    output_dir = Path(".dev/scholar_test_openathens")
    output_dir.mkdir(exist_ok=True)

    try:
        pdf_path = scholar.download_pdf(
            paper,
            output_dir=output_dir,
            force=True  # Force re-download
        )

        if pdf_path:
            print(f"✓ Downloaded to: {pdf_path}")
            print(f"  File size: {pdf_path.stat().st_size} bytes")
        else:
            print("✗ Download failed!")

            # Check if OpenAthens authenticated
            if hasattr(scholar, '_pdf_downloader') and scholar._pdf_downloader:
                downloader = scholar._pdf_downloader
                if hasattr(downloader, 'openathens_authenticator') and downloader.openathens_authenticator:
                    auth = downloader.openathens_authenticator
                    is_auth = auth.is_authenticated()
                    print(f"\nOpenAthens authenticated: {is_auth}")
                    if is_auth:
                        is_verified, details = auth.verify_authentication()
                        print(f"Authentication verification: {details}")

    except Exception as e:
        print(f"ERROR during download: {e}")
        import traceback
        traceback.print_exc()

def main():
    """Test multiple DOIs."""
    test_dois = [
        "10.3389/fnins.2019.00885",     # Open access Frontiers paper
        "10.1016/j.yebeh.2024.109736",  # User requested DOI (likely paywalled)
    ]

    for doi in test_dois:
        test_scholar_download_with_openathens(doi)
        print("\n" + "="*60 + "\n")

if __name__ == "__main__":
    main()
