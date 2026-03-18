#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-07-23 13:39:03 (ywatanabe)"
# File: ./examples/scholar/download_dois_sync_example.py
# ----------------------------------------
"""
Example: Synchronous PDF download from DOIs

This example shows how to use the synchronous version of dois_to_local_pdfs
for simpler scripts that don't need async/await.
"""

from scitex.scholar import dois_to_local_pdfs

def main():
    print("SciTeX Scholar - Synchronous DOI Download Example")
    print("=" * 50)

    # Simple list of DOIs to download
    dois = [
        "10.1162/jocn.2008.21020",  # Example neuroscience paper
        "10.1093/brain/awt276",     # Example brain research
        "10.1038/nature12373"       # Example Nature paper
    ]

    print(f"\nDownloading {len(dois)} papers...")

    # Download PDFs synchronously
    results = dois_to_local_pdfs(
        dois,
        download_dir="./sync_example_pdfs",
        max_workers=2,
        show_progress=True
    )

    # Display results
    print(f"\n{'='*50}")
    print(f"Successfully downloaded: {results['successful']} PDFs")
    print(f"Failed downloads: {results['failed']}")

    # Show individual results
    print("\nDetailed results:")
    for result in results['results']:
        status = "✓" if result['success'] else "✗"
        print(f"{status} {result['doi']}")
        if result['success']:
            print(f"   -> {result['filename']}")
        else:
            print(f"   -> {result['message']}")

    # Show file mapping
    if results['downloaded_files']:
        print("\nDOI to file mapping:")
        for doi, filepath in results['downloaded_files'].items():
            print(f"  {doi}")
            print(f"    -> {filepath}")

    print(f"\n{'='*50}")
    print("Note: Ensure you have the rights to download these papers.")
    print("Sci-Hub access may vary by region.")


if __name__ == "__main__":
    main()
