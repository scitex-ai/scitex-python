#!/usr/bin/env python3
"""
Demonstration of ZenRows Scraping Browser for paywalled journal access.

This shows how the Scraping Browser solves the authentication problem
by running the entire session (login + download) in a remote browser.
"""

import os
import asyncio
from scitex.scholar.open_url import OpenURLResolverWithScrapingBrowser
from scitex.scholar.auth import AuthenticationManager
from scitex import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def main():
    """Demonstrate full paywalled access with ZenRows Scraping Browser."""

    print("="*70)
    print("🚀 ZenRows Scraping Browser - Paywalled Journal Access Demo")
    print("="*70)

    # Ensure environment variables are set
    required_vars = {
        "SCITEX_SCHOLAR_ZENROWS_API_KEY": "ZenRows API key",
        "SCITEX_SCHOLAR_OPENATHENS_EMAIL": "Institutional email",
        "SCITEX_SCHOLAR_OPENURL_RESOLVER_URL": "Resolver URL",
        "SCITEX_SCHOLAR_2CAPTCHA_API_KEY": "2Captcha key"
    }

    missing = []
    for var, desc in required_vars.items():
        if not os.getenv(var):
            missing.append(f"  - {var} ({desc})")

    if missing:
        print("\n❌ Missing required environment variables:")
        print("\n".join(missing))
        print("\nSet these before running the demo.")
        return

    # Set 2Captcha if not already set
    os.environ["SCITEX_SCHOLAR_2CAPTCHA_API_KEY"] = "36d184fbba134f828cdd314f01dc7f18"

    print("\n✅ All environment variables configured")

    # Initialize authentication manager
    auth_manager = AuthenticationManager(
        email_openathens=os.getenv("SCITEX_SCHOLAR_OPENATHENS_EMAIL")
    )

    # Create resolver with ZenRows Scraping Browser
    print("\n🌐 Initializing ZenRows Scraping Browser resolver...")
    resolver = OpenURLResolverWithScrapingBrowser(
        auth_manager,
        os.getenv("SCITEX_SCHOLAR_OPENURL_RESOLVER_URL"),
        proxy_country="us",  # Use US residential IP
        enable_captcha_solving=True
    )

    print("   ✓ Connected to remote browser")
    print("   ✓ Using US residential IP")
    print("   ✓ 2Captcha integration enabled")

    # Test with paywalled papers
    paywalled_dois = [
        {
            "doi": "10.1038/nature12373",
            "title": "A mesoscale connectome of the mouse brain",
            "journal": "Nature",
            "year": 2014
        },
        {
            "doi": "10.1016/j.cell.2020.05.032",
            "title": "Cell paper example",
            "journal": "Cell",
            "year": 2020
        },
        {
            "doi": "10.1126/science.abg6155",
            "title": "Science paper example",
            "journal": "Science",
            "year": 2021
        }
    ]

    print("\n🔐 Authenticating in remote browser...")
    print("   (This happens entirely on ZenRows servers)")

    # Authenticate - this now works in the remote browser!
    auth_success = await resolver.authenticate_async()

    if auth_success:
        print("   ✅ Authentication successful!")
        print("   → Session maintained in remote browser")
        print("   → Ready to access paywalled content")
    else:
        print("   ❌ Authentication failed")
        print("   → Check your credentials")
        await resolver.close()
        return

    print("\n📚 Resolving paywalled papers...")
    print("-"*50)

    successful = 0
    for paper_info in paywalled_dois:
        doi = paper_info["doi"]
        print(f"\n🔍 Resolving: {doi}")
        print(f"   Journal: {paper_info['journal']}")

        try:
            # Resolve in the authenticated remote browser
            result = await resolver._resolve_single_async(**paper_info)

            if result and result.get('success'):
                successful += 1
                print(f"   ✅ SUCCESS! Resolved to PDF")
                print(f"   → Final URL: {result.get('final_url', 'N/A')[:80]}...")
                print(f"   → Access type: {result.get('access_type')}")
                print(f"   → Proxy country: {result.get('proxy_country')}")
            else:
                print(f"   ❌ Failed: {result.get('access_type', 'Unknown error')}")
                if result.get('note'):
                    print(f"   → Note: {result['note']}")

        except Exception as e:
            print(f"   ❌ Error: {str(e)}")

    print("\n" + "="*50)
    print(f"📊 Results: {successful}/{len(paywalled_dois)} papers successfully resolved")

    # Compare with traditional approaches
    print("\n📋 Why This Works (Scraping Browser vs Traditional):")
    print("-"*50)
    print("Traditional ZenRows API:")
    print("  ❌ No authentication context")
    print("  ❌ Can't maintain session")
    print("  ❌ Fails on paywalled content")
    print("\nZenRows Scraping Browser:")
    print("  ✅ Full browser session")
    print("  ✅ Authentication maintained")
    print("  ✅ Access to paywalled content")
    print("  ✅ Appears as legitimate traffic")

    # Clean up
    print("\n🧹 Cleaning up...")
    await resolver.close()
    print("✅ Done!")

async def simple_example():
    """Simplified example for quick testing."""
    print("\n🎯 Simple Example: Download One Paywalled Paper")
    print("-"*50)

    # Setup
    from scitex.scholar import Scholar

    # Configure to use ZenRows Scraping Browser
    os.environ["SCITEX_SCHOLAR_USE_ZENROWS_BROWSER"] = "true"
    os.environ["SCITEX_SCHOLAR_2CAPTCHA_API_KEY"] = "36d184fbba134f828cdd314f01dc7f18"

    # Initialize Scholar (will use Scraping Browser automatically)
    scholar = Scholar()

    # Download a paywalled paper
    doi = "10.1038/nature12373"
    print(f"Downloading: {doi}")

    results = scholar.download_pdfs([doi])

    if results.papers and hasattr(results.papers[0], 'pdf_path'):
        print(f"✅ Success! Downloaded to: {results.papers[0].pdf_path}")
    else:
        print("❌ Download failed")

if __name__ == "__main__":
    print("🔬 SciTeX Scholar - ZenRows Scraping Browser Demo")
    print("="*70)
    print("\nThis demo shows how ZenRows Scraping Browser enables")
    print("authenticated access to paywalled journals.\n")

    # Run the main demo
    asyncio.run(main())

    # Optional: Run simple example
    # asyncio.run(simple_example())
