#!/usr/bin/env python3
"""
Example demonstrating automatic OpenURL resolver handling in SciTeX Scholar.

This shows how the Scholar module automatically uses OpenURL resolver
as part of its download strategies without manual intervention.
"""

import os
from scitex.scholar import Scholar

def main():
    # Set up API keys (ZenRows is optional)
    # If SCITEX_SCHOLAR_ZENROWS_API_KEY is set, it will automatically use ZenRows
    os.environ["SCITEX_SCHOLAR_2CAPTCHA_API_KEY"] = "36d184fbba134f828cdd314f01dc7f18"

    # Initialize Scholar - it automatically sets up all download strategies
    # including OpenURL resolver
    scholar = Scholar()

    # Search for papers
    print("Searching for papers...")
    papers = scholar.search("deep learning neuroscience", limit=5)

    # Download PDFs - Scholar automatically tries multiple strategies:
    # 1. ZenRows (if API key is available)
    # 2. Lean Library
    # 3. OpenURL Resolver (institutional access)
    # 4. Zotero translators
    # 5. Direct patterns
    # 6. Playwright
    print("\nDownloading PDFs (automatic strategy selection)...")
    results = scholar.download_pdfs(papers)

    # Show which methods were used
    print("\n=== Download Results ===")
    for paper in results.papers:
        if hasattr(paper, 'pdf_source') and paper.pdf_source:
            print(f"\n📄 {paper.title[:60]}...")
            print(f"   Method used: {paper.pdf_source}")
            if hasattr(paper, 'pdf_path') and paper.pdf_path:
                print(f"   Saved to: {paper.pdf_path}")

    # The Scholar module automatically:
    # - Detects if ZenRows API key is available and uses it
    # - Falls back to OpenURL resolver for institutional access
    # - Tries other methods if those fail
    # - No manual URL resolver configuration needed!

    print("\n✅ Scholar automatically handled URL resolution!")
    print("   No manual OpenURL resolver setup required.")

if __name__ == "__main__":
    main()
