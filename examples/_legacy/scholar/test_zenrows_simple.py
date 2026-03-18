#!/usr/bin/env python3
"""
Simple test of ZenRows Scraping Browser with Scholar module.

Shows how to use ZenRows backend for institutional access.
Manual login is supported when credentials are not provided.
"""

import asyncio
import os
from pathlib import Path
from scitex.scholar import Scholar, ScholarConfig

async def test_zenrows_scholar():
    """Test Scholar with ZenRows browser backend."""

    # Check environment variables
    print("Checking environment variables...")
    backend = os.getenv("SCITEX_SCHOLAR_BROWSER_BACKEND", "local")
    api_key = os.getenv("SCITEX_SCHOLAR_ZENROWS_API_KEY")

    if backend != "zenrows" or not api_key:
        print("\nPlease set environment variables:")
        print("export SCITEX_SCHOLAR_BROWSER_BACKEND=zenrows")
        print("export SCITEX_SCHOLAR_ZENROWS_API_KEY=your_key")
        return

    print(f"✓ Browser backend: {backend}")
    print(f"✓ ZenRows API key: {api_key[:10]}...")
    print(f"✓ Proxy country: {os.getenv('SCITEX_SCHOLAR_ZENROWS_PROXY_COUNTRY', 'us')}")

    # Create Scholar with ZenRows backend
    print("\nCreating Scholar instance with ZenRows backend...")

    # Option 1: Let it use environment variables automatically
    scholar = Scholar()

    # Option 2: Explicitly set config
    # config = ScholarConfig(
    #     browser_backend="zenrows",
    #     zenrows_proxy_country="au"
    # )
    # scholar = Scholar(config=config)

    # Test DOIs
    test_dois = [
        "10.1038/s41586-023-06516-4",  # Nature paper
        "10.1126/science.abj8754",      # Science paper
    ]

    print("\n" + "="*60)
    print("TESTING ZENROWS INTEGRATION")
    print("="*60)
    print("The ZenRows browser will be used for all operations.")
    print("If authentication is needed, you can login manually.")
    print("="*60 + "\n")

    for doi in test_dois:
        print(f"\nSearching for DOI: {doi}")
        try:
            # Search for the paper
            papers = await scholar.search_async(doi)

            if papers:
                paper = papers[0]
                print(f"✓ Found: {paper.title[:60]}...")
                print(f"  Journal: {paper.journal}")
                print(f"  Year: {paper.year}")

                # Try to get PDF URL
                if hasattr(paper, 'pdf_url') and paper.pdf_url:
                    print(f"  PDF URL: {paper.pdf_url}")
                else:
                    print("  PDF URL: Not found (may need authentication)")

            else:
                print("✗ Paper not found")

        except Exception as e:
            print(f"✗ Error: {e}")

    # Test PDF download with manual authentication
    print("\n" + "="*60)
    print("TESTING PDF DOWNLOAD")
    print("="*60)

    try:
        # This will attempt to download PDFs
        # If authentication is needed, a browser window will open
        print("\nAttempting to download PDFs...")
        print("If prompted, please login to your institutional account.")

        pdf_dir = Path("./test_pdfs")
        pdf_dir.mkdir(exist_ok=True)

        papers = await scholar.download_pdfs_async(
            test_dois[:1],  # Just test one
            pdf_dir=pdf_dir
        )

        if papers and papers[0].get('pdf_path'):
            print(f"\n✓ PDF downloaded successfully!")
            print(f"  Location: {papers[0]['pdf_path']}")
        else:
            print("\n✗ PDF download failed or requires manual authentication")

    except Exception as e:
        print(f"\n✗ Download error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("ZenRows Scholar Integration Test")
    print("================================\n")

    print("This test uses the ZenRows Scraping Browser for all operations.")
    print("Benefits:")
    print("- Bypass anti-bot measures")
    print("- Handle JavaScript-heavy sites")
    print("- Maintain session across requests")
    print("- Support manual login when needed\n")

    asyncio.run(test_zenrows_scholar())
