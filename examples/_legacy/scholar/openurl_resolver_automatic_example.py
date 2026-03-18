#!/usr/bin/env python3
"""
Example showing OpenURL resolver working automatically within Scholar.

No manual OpenURL resolver setup needed - Scholar handles it all!
"""

import os
from scitex.scholar import Scholar

def main():
    # Set 2Captcha for CAPTCHA solving
    os.environ["SCITEX_SCHOLAR_2CAPTCHA_API_KEY"] = "36d184fbba134f828cdd314f01dc7f18"

    # Optional: Set ZenRows if you have it
    # os.environ["SCITEX_SCHOLAR_ZENROWS_API_KEY"] = "your_key"

    # Initialize Scholar
    print("Initializing Scholar with automatic URL resolver...")
    scholar = Scholar()

    # Example 1: Download a paper by DOI
    print("\n=== Example 1: Download by DOI ===")
    doi = "10.1016/j.neuroimage.2019.116309"

    print(f"Downloading paper with DOI: {doi}")
    print("Scholar will automatically try OpenURL resolver if needed...")

    result = scholar.download_pdfs([doi])

    if result.papers:
        paper = result.papers[0]
        print(f"\n✅ Success!")
        print(f"   Method used: {getattr(paper, 'pdf_source', 'Unknown')}")
        if hasattr(paper, 'pdf_path'):
            print(f"   Saved to: {paper.pdf_path}")

    # Example 2: Search and download with automatic resolver
    print("\n\n=== Example 2: Search and Download ===")
    papers = scholar.search("fMRI preprocessing", limit=3)

    print(f"\nFound {len(papers)} papers")
    print("Downloading all (URL resolver will be used automatically if needed)...")

    results = scholar.download_pdfs(papers)

    print("\n📊 Download Statistics:")
    methods_used = {}
    for paper in results.papers:
        if hasattr(paper, 'pdf_source'):
            method = paper.pdf_source
            methods_used[method] = methods_used.get(method, 0) + 1

    for method, count in methods_used.items():
        print(f"   {method}: {count} papers")

    # Example 3: Show that manual URL resolver still works
    print("\n\n=== Example 3: Manual URL Resolver (for comparison) ===")
    print("You CAN still use URL resolver manually if needed:")

    from scitex.scholar.open_url import OpenURLResolver

    # Manual usage (not necessary with Scholar!)
    resolver = OpenURLResolver("https://resolver.your-institution.edu")
    pdf_url = resolver.resolve_doi_sync("10.1234/example")
    print(f"Manual resolution: {pdf_url}")

    print("\n✨ But with Scholar, you don't need to do this!")
    print("   Scholar handles URL resolution automatically.")

if __name__ == "__main__":
    main()

    print("\n\n" + "="*60)
    print("🎯 Key Takeaways:")
    print("="*60)
    print("1. Scholar automatically integrates OpenURL resolver")
    print("2. No manual URL resolver configuration needed")
    print("3. It's tried automatically when downloading papers")
    print("4. Works seamlessly with or without ZenRows")
    print("5. You can still use manual resolver if needed")
    print("="*60)
