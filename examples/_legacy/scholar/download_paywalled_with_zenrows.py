#!/usr/bin/env python3
"""
Download paywalled papers using ZenRows Scraping Browser.

This demonstrates the complete workflow for accessing paywalled content
with institutional authentication through a remote browser.
"""

import os
from scitex.scholar import Scholar

# Configure environment for ZenRows Scraping Browser
os.environ["SCITEX_SCHOLAR_BROWSER_BACKEND"] = "zenrows"
os.environ["SCITEX_SCHOLAR_ZENROWS_API_KEY"] = "822225799f9a4d847163f397ef86bb81b3f5ceb5"
os.environ["SCITEX_SCHOLAR_ZENROWS_PROXY_COUNTRY"] = "au"
os.environ["SCITEX_SCHOLAR_2CAPTCHA_API_KEY"] = "36d184fbba134f828cdd314f01dc7f18"

def download_paywalled_papers_with_zenrows():
    """Download paywalled papers using ZenRows remote browser."""

    print("🌐 SciTeX Scholar - Paywalled Access via ZenRows")
    print("="*60)
    print("\nUsing ZenRows Scraping Browser for:")
    print("  ✓ Remote browser session")
    print("  ✓ Australian residential IP")
    print("  ✓ Full authentication support")
    print("  ✓ Anti-bot bypass")

    # Initialize Scholar (automatically uses ZenRows from env vars)
    scholar = Scholar()

    print(f"\n📍 Configuration:")
    print(f"   Browser: {scholar.config.browser_backend}")
    print(f"   Proxy: {scholar.config.zenrows_proxy_country}")

    # Check authentication
    print("\n🔐 Checking authentication...")
    if scholar.config.openathens_enabled:
        # Authentication will happen in ZenRows remote browser!
        if not scholar.is_openathens_authenticated():
            print("   🌐 Opening REMOTE browser for authentication...")
            print("   → Browser runs on ZenRows servers")
            print("   → Appears as Australian residential IP")
            print("   → Session maintained remotely")

            success = scholar.authenticate_openathens()
            if success:
                print("   ✅ Authenticated in remote browser!")
            else:
                print("   ❌ Authentication failed")
                return
        else:
            print("   ✅ Already authenticated!")

    # Download paywalled papers
    print("\n📥 Downloading paywalled papers...")

    paywalled_dois = [
        "10.1038/nature12373",  # Nature
        "10.1016/j.cell.2020.05.032",  # Cell
        "10.1126/science.abg6155",  # Science
    ]

    # The magic happens here:
    # 1. Scholar uses ZenRows browser for all operations
    # 2. Authentication session is maintained in remote browser
    # 3. Downloads happen through authenticated remote session
    # 4. Full access to paywalled content!

    results = scholar.download_pdfs(paywalled_dois, show_progress=True)

    # Show results
    print("\n📊 Results:")
    print("-"*50)

    for paper in results.papers:
        if hasattr(paper, 'pdf_path') and paper.pdf_path:
            print(f"✅ {paper.title[:50]}...")
            print(f"   File: {paper.pdf_path.name}")
            print(f"   Method: {getattr(paper, 'pdf_source', 'Unknown')}")
        else:
            print(f"❌ Failed: {getattr(paper, 'doi', 'Unknown')}")

    print("\n🎉 The ZenRows Difference:")
    print("  • Authentication happened in remote browser")
    print("  • Session preserved throughout download")
    print("  • Accessed paywalled content successfully")
    print("  • No cookie transfer issues!")

def quick_test():
    """Quick test to verify ZenRows is working."""
    print("\n\n🚀 Quick ZenRows Test")
    print("="*40)

    # Set backend
    os.environ["SCITEX_SCHOLAR_BROWSER_BACKEND"] = "zenrows"

    # Test with a single DOI
    scholar = Scholar()

    doi = "10.1038/nature12373"
    print(f"Testing with: {doi}")

    # This will use ZenRows for everything!
    result = scholar.download_pdfs([doi])

    if result.papers and hasattr(result.papers[0], 'pdf_path'):
        print("✅ Success! ZenRows browser worked!")
    else:
        print("❌ Download failed")

if __name__ == "__main__":
    # Run main example
    download_paywalled_papers_with_zenrows()

    # Run quick test
    quick_test()

    print("\n\n💡 Configuration Summary:")
    print("="*50)
    print("export SCITEX_SCHOLAR_BROWSER_BACKEND='zenrows'")
    print("export SCITEX_SCHOLAR_ZENROWS_API_KEY='your_key'")
    print("export SCITEX_SCHOLAR_ZENROWS_PROXY_COUNTRY='au'")
    print("export SCITEX_SCHOLAR_2CAPTCHA_API_KEY='your_key'")
    print("="*50)
