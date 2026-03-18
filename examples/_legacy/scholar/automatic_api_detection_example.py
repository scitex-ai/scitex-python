#!/usr/bin/env python3
"""
Example demonstrating automatic API detection in SciTeX Scholar.

Scholar automatically detects which APIs are available based on environment
variables and configures download strategies accordingly.
"""

import os
from scitex.scholar import Scholar, ScholarConfig

def demonstrate_automatic_configuration():
    """Show how Scholar automatically configures based on available APIs."""

    print("=== SciTeX Scholar - Automatic API Detection ===\n")

    # Set 2Captcha API key (for CAPTCHA solving)
    os.environ["SCITEX_SCHOLAR_2CAPTCHA_API_KEY"] = "36d184fbba134f828cdd314f01dc7f18"
    print("✅ 2Captcha API key set")

    # Optionally set ZenRows API key
    # If not set, Scholar won't use ZenRows
    zenrows_key = os.getenv("SCITEX_SCHOLAR_ZENROWS_API_KEY")
    if zenrows_key:
        print(f"✅ ZenRows API key detected: {zenrows_key[:8]}...")
    else:
        print("ℹ️  ZenRows API key not set - will use standard methods")

    # Initialize Scholar - it automatically detects available APIs
    print("\nInitializing Scholar...")
    scholar = Scholar()

    # The PDFDownloader inside Scholar automatically:
    # 1. Detects if ZenRows API key is available
    # 2. Configures OpenURL resolver (with or without ZenRows)
    # 3. Sets up all download strategies in the right order

    print("\n📋 Download strategies configured (in priority order):")
    print("1. ZenRows" + (" ✓" if zenrows_key else " ✗ (no API key)"))
    print("2. Lean Library ✓")
    print("3. OpenURL Resolver ✓ (institutional access)")
    print("4. Zotero translators ✓")
    print("5. Direct patterns ✓")
    print("6. Playwright ✓")

    # Example: Search and download
    print("\n🔍 Searching for papers...")
    papers = scholar.search("quantum computing", limit=3)

    print(f"\nFound {len(papers)} papers")

    # Download PDFs - automatic strategy selection
    print("\n📥 Downloading PDFs...")
    print("Scholar will automatically try strategies based on available APIs")

    results = scholar.download_pdfs(papers, show_progress=True)

    # Show results
    print("\n=== Download Results ===")
    for paper in results.papers:
        if hasattr(paper, 'pdf_path') and paper.pdf_path:
            method = getattr(paper, 'pdf_source', 'Unknown')
            print(f"\n✅ {paper.title[:50]}...")
            print(f"   Method: {method}")
            print(f"   File: {paper.pdf_path.name}")

def demonstrate_manual_zenrows_toggle():
    """Show how to manually control ZenRows usage."""

    print("\n\n=== Manual ZenRows Control ===\n")

    # Method 1: Set environment variable
    os.environ["SCITEX_SCHOLAR_ZENROWS_API_KEY"] = "your_api_key_here"
    scholar1 = Scholar()  # Will use ZenRows

    # Method 2: Remove environment variable
    os.environ.pop("SCITEX_SCHOLAR_ZENROWS_API_KEY", None)
    scholar2 = Scholar()  # Won't use ZenRows

    print("✅ ZenRows usage is automatically controlled by API key presence")
    print("   No need for a separate USE_ZENROWS flag!")

def demonstrate_url_resolver_integration():
    """Show that URL resolver is always integrated automatically."""

    print("\n\n=== Automatic URL Resolver Integration ===\n")

    # Initialize Scholar
    scholar = Scholar()

    # Search for a paper
    papers = scholar.search("machine learning", limit=1)

    if papers:
        paper = papers[0]
        print(f"Paper: {paper.title}")
        print(f"DOI: {paper.doi or 'No DOI'}")

        # Download - Scholar automatically uses URL resolver when appropriate
        print("\nDownloading (URL resolver will be tried automatically)...")
        result = scholar.download_pdfs([paper])

        if result.papers:
            downloaded = result.papers[0]
            if hasattr(downloaded, 'pdf_source'):
                print(f"\n✅ Downloaded using: {downloaded.pdf_source}")
                if downloaded.pdf_source == "OpenURL Resolver":
                    print("   URL resolver was used automatically!")

if __name__ == "__main__":
    # Run demonstrations
    demonstrate_automatic_configuration()
    demonstrate_manual_zenrows_toggle()
    demonstrate_url_resolver_integration()

    print("\n\n🎉 Summary:")
    print("- Scholar automatically detects available APIs")
    print("- ZenRows is used if API key is present")
    print("- URL resolver is always integrated")
    print("- No manual configuration needed!")
