#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-07-23 13:39:03 (ywatanabe)"
# File: ./examples/scholar/download_dois_example.py
# ----------------------------------------
"""
Example: Asynchronously download PDFs from DOIs using Sci-Hub integration

This example demonstrates how to use the dois_to_local_pdfs_async function
to download PDFs that may not be available through open access channels.
"""

import asyncio
from scitex.scholar import Scholar, dois_to_local_pdfs_async


async def main():
    print("SciTeX Scholar - DOI to PDF Download Example")
    print("=" * 50)

    # Example 1: Download from list of DOIs
    print("\n1. Downloading from DOI list:")
    dois = [
        "10.1162/jocn.2008.21020",
        "10.1093/brain/awt276",
        "10.1038/nature12373"
    ]

    results = await dois_to_local_pdfs_async(
        dois,
        download_dir="./example_pdfs",
        max_workers=2
    )

    print(f"\nDownloaded {results['successful']} PDFs successfully")
    print(f"Failed: {results['failed']}")

    # Example 2: Download from search results
    print("\n\n2. Downloading from search results:")
    scholar = Scholar()

    # Search for papers
    papers = scholar.search("machine learning neuroscience", limit=5)
    print(f"Found {len(papers)} papers")

    # Filter papers with DOIs
    papers_with_dois = [p for p in papers.papers if p.doi]
    print(f"Papers with DOIs: {len(papers_with_dois)}")

    if papers_with_dois:
        # Download PDFs
        results = await dois_to_local_pdfs_async(
            papers_with_dois,
            download_dir="./search_pdfs",
            max_workers=3
        )

        print(f"\nDownloaded {results['successful']} PDFs from search results")
        print(f"Failed: {results['failed']}")

        # Show downloaded files
        if results['downloaded_files']:
            print("\nDownloaded files:")
            for doi, filepath in results['downloaded_files'].items():
                print(f"  - {doi} -> {filepath}")

    # Example 3: Custom configuration
    print("\n\n3. Custom download configuration:")

    # You can also specify custom parameters
    results = await dois_to_local_pdfs_async(
        ["10.1016/j.cell.2019.05.031"],  # Example high-impact paper
        download_dir="./custom_pdfs",
        max_workers=1,
        timeout=60,  # Longer timeout for slow connections
        max_retries=5  # More retries for reliability
    )

    if results['successful'] > 0:
        print("Successfully downloaded high-impact paper!")

    print("\n" + "=" * 50)
    print("Note: This uses Sci-Hub which may not be accessible in all regions.")
    print("Please ensure you have the rights to download these papers.")


if __name__ == "__main__":
    # Run the async main function
    asyncio.run(main())
