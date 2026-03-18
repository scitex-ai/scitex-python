#!/usr/bin/env python3
"""Simple test to check PDFDownloader directly."""

from scitex.scholar._PDFDownloader import PDFDownloader
from pathlib import Path
import asyncio

async def test_download():
    # Create downloader with ethical acknowledgment
    downloader = PDFDownloader(
        download_dir=Path(".dev/test_pdfs"),
        use_scihub=True,
        acknowledge_ethical_usage=True
    )

    # Test DOIs
    test_dois = [
        "10.1371/journal.pone.0029609",  # Known open access
        "10.1038/s41586-023-06670-9",     # Nature paper (likely paywalled)
    ]

    print("Testing PDF downloads...")
    for doi in test_dois:
        print(f"\nTrying DOI: {doi}")
        try:
            result = await downloader.download(doi)
            if result:
                print(f"  ✓ Success: {result}")
            else:
                print(f"  ✗ Failed: No file returned")
        except Exception as e:
            print(f"  ✗ Error: {e}")

# Run the test
asyncio.run(test_download())
