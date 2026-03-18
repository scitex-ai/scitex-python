#!/usr/bin/env python3
"""
Improved Scholar download with rate limiting and OpenURL resolver
Based on University of Melbourne library feedback
"""

import time
from pathlib import Path
from scitex.scholar import Scholar, ScholarConfig

def download_with_limits():
    """Download papers respecting publisher limits."""

    # Configure with improvements
    config = ScholarConfig(
        pdf_dir="./pdfs",
        enable_auto_download=False,
        enable_auto_enrich=False,
        use_lean_library=True,  # Best option for institutional access
        acknowledge_scihub_ethical_usage=True,  # Fallback for older papers
    )

    scholar = Scholar(config)

    # Search for papers
    papers = scholar.search(
        "epilepsy detection machine learning",
        limit=10,
        sources=["pubmed", "crossref"]  # Avoid Google Scholar (blocks)
    )

    print(f"Found {len(papers)} papers")

    # Download with rate limiting
    downloaded = 0
    failed = 0

    for i, paper in enumerate(papers.papers):
        if not paper.doi:
            print(f"Skipping {i+1}: No DOI")
            continue

        print(f"\n[{i+1}/{len(papers)}] Downloading: {paper.title[:50]}...")

        # Rate limit: 10 downloads per minute (6 seconds between)
        if i > 0:
            print("   Waiting 6 seconds (rate limit)...")
            time.sleep(6)

        # Try download
        result = scholar.download_pdfs(
            paper,
            show_progress=True
        )

        if len(result) > 0:
            downloaded += 1
            print("   ✅ Success")
        else:
            failed += 1
            print("   ❌ Failed - may need manual download")

        # Stop if too many failures (likely being blocked)
        if failed > 3:
            print("\n⚠️  Multiple failures - stopping to avoid blocking")
            break

    print(f"\n{'='*60}")
    print(f"Summary: {downloaded} downloaded, {failed} failed")
    print("\nFor failed downloads:")
    print("1. Install Lean Library browser extension")
    print("2. Or manually download through your institution")
    print("3. Check the library's vendor permissions spreadsheet")

if __name__ == "__main__":
    print("Scholar Download with Rate Limiting")
    print("Based on University of Melbourne Library recommendations")
    print("="*60)

    download_with_limits()
