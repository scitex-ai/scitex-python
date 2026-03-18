#!/usr/bin/env python3
"""
Simple example: Download paywalled papers correctly.

This shows the easiest way to download paywalled journal articles.
"""

from scitex.scholar import Scholar
import os

# Set your 2Captcha key (helps with some publishers)
os.environ["SCITEX_SCHOLAR_2CAPTCHA_API_KEY"] = "36d184fbba134f828cdd314f01dc7f18"

def download_paywalled_papers():
    """Download paywalled papers with proper authentication."""

    print("🔬 SciTeX Scholar - Paywalled Paper Download")
    print("="*50)

    # Step 1: Initialize Scholar
    scholar = Scholar()

    # Step 2: Check authentication
    print("\n1️⃣ Checking authentication...")
    if scholar.config.openathens_enabled:
        if not scholar.is_openathens_authenticated():
            print("   🔐 Not authenticated. Opening browser for login...")
            success = scholar.authenticate_openathens()
            if success:
                print("   ✅ Authentication successful!")
            else:
                print("   ❌ Authentication failed. Cannot access paywalled content.")
                return
        else:
            print("   ✅ Already authenticated!")
    else:
        print("   ⚠️  OpenAthens not configured. Set SCITEX_SCHOLAR_OPENATHENS_EMAIL")

    # Step 3: Download paywalled papers
    print("\n2️⃣ Downloading paywalled papers...")

    # Example paywalled DOIs
    paywalled_dois = [
        "10.1038/nature12373",  # Nature - "A mesoscale connectome of the mouse brain"
        "10.1016/j.cell.2020.05.032",  # Cell - Example paper
        "10.1126/science.abg6155",  # Science - Example paper
    ]

    # Download all at once (most efficient)
    results = scholar.download_pdfs(paywalled_dois)

    # Step 4: Check results
    print("\n3️⃣ Results:")
    print("-"*50)

    success_count = 0
    for paper in results.papers:
        if hasattr(paper, 'pdf_path') and paper.pdf_path:
            success_count += 1
            print(f"✅ Downloaded: {paper.title[:60]}...")
            print(f"   File: {paper.pdf_path.name}")
            print(f"   Method: {getattr(paper, 'pdf_source', 'Unknown')}")
        else:
            doi = getattr(paper, 'doi', 'Unknown DOI')
            print(f"❌ Failed: {doi}")

    print(f"\n📊 Summary: {success_count}/{len(paywalled_dois)} papers downloaded")

    # Step 5: Alternative - search and download
    print("\n\n4️⃣ Alternative: Search and download")
    print("-"*50)

    # Search for papers
    papers = scholar.search("neuroscience connectome", limit=3)
    print(f"Found {len(papers)} papers")

    # Download them (will use authentication automatically)
    download_results = scholar.download_pdfs(papers)

    downloaded = sum(1 for p in download_results.papers
                    if hasattr(p, 'pdf_path') and p.pdf_path)
    print(f"Downloaded {downloaded}/{len(papers)} papers from search")

def main():
    """Run the example."""
    try:
        download_paywalled_papers()
    except KeyboardInterrupt:
        print("\n\n⚠️  Download cancelled by user")
    except Exception as e:
        print(f"\n\n❌ Error: {e}")
        print("\nTroubleshooting:")
        print("1. Check your internet connection")
        print("2. Verify SCITEX_SCHOLAR_OPENATHENS_EMAIL is set")
        print("3. Ensure SCITEX_SCHOLAR_OPENURL_RESOLVER_URL is correct")
        print("4. Try authenticating manually first")

if __name__ == "__main__":
    main()

    print("\n\n" + "="*70)
    print("💡 Remember:")
    print("- Paywalled access requires institutional authentication")
    print("- Use Scholar (not ZenRows) for paywalled content")
    print("- Authenticate once, download many")
    print("- Your institution must have journal subscriptions")
    print("="*70)
