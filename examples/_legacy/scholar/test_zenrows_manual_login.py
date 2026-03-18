#!/usr/bin/env python3
"""
Test ZenRows Scraping Browser with manual login support.

This script shows how manual intervention works with ZenRows browser.
You can manually log in when prompted, and the session will be maintained.
"""

import asyncio
import os
from scitex.scholar import ScholarConfig
from scitex.scholar.open_url import OpenURLResolver
from scitex.scholar.auth import AuthenticationManager

async def test_zenrows_with_manual_login():
    """Test OpenURL resolver with ZenRows browser and manual login."""

    # Check environment variables
    print("Checking environment variables...")
    browser_backend = os.getenv("SCITEX_SCHOLAR_BROWSER_BACKEND", "local")
    zenrows_key = os.getenv("SCITEX_SCHOLAR_ZENROWS_API_KEY")

    if browser_backend != "zenrows" or not zenrows_key:
        print("Error: Please set environment variables first:")
        print("export SCITEX_SCHOLAR_BROWSER_BACKEND=zenrows")
        print("export SCITEX_SCHOLAR_ZENROWS_API_KEY=your_key")
        return

    print(f"✓ Browser backend: {browser_backend}")
    print(f"✓ ZenRows API key: {zenrows_key[:10]}...")

    # Create config
    config = ScholarConfig(
        browser_backend="zenrows",
        zenrows_proxy_country=os.getenv("SCITEX_SCHOLAR_ZENROWS_PROXY_COUNTRY", "au"),
        # Don't set username/password - we'll login manually
        openathens_username=None,
        openathens_password=None,
        openurl_resolver="https://go.openathens.net/redirector/unisa.edu.au"
    )

    print("\nCreating authentication manager...")
    auth_manager = AuthenticationManager(config)

    # Test DOI
    test_doi = "10.1038/s41586-023-06516-4"

    print(f"\nTesting DOI: {test_doi}")
    print("Creating OpenURL resolver with ZenRows backend...")

    resolver = OpenURLResolver(
        auth_manager=auth_manager,
        resolver_url=config.openurl_resolver,
        browser_backend=config.browser_backend,
        zenrows_api_key=config.zenrows_api_key,
        proxy_country=config.zenrows_proxy_country
    )

    try:
        print("\nInitializing browser connection...")
        await resolver.browser.initialize()

        print("\n" + "="*60)
        print("MANUAL LOGIN INSTRUCTIONS:")
        print("="*60)
        print("1. A browser window will open on ZenRows servers")
        print("2. You'll see the institutional login page")
        print("3. Manually enter your credentials and complete login")
        print("4. Once logged in, the script will continue automatically")
        print("5. The session will be maintained for subsequent requests")
        print("="*60 + "\n")

        print("Attempting to resolve DOI through institutional access...")
        result = await resolver.resolve(test_doi)

        if result.get("pdf_url"):
            print(f"\n✓ Success! PDF URL found: {result['pdf_url']}")
            print(f"Title: {result.get('title', 'Unknown')}")
            print(f"Source: Resolved via {result.get('source', 'OpenURL')}")
        else:
            print(f"\n✗ No PDF URL found. Full result: {result}")

    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        print("\nCleaning up...")
        await resolver.browser.close()

if __name__ == "__main__":
    print("ZenRows Manual Login Test")
    print("=" * 50)
    print("\nThis test allows manual login for institutional access.")
    print("The ZenRows browser will maintain your session.\n")

    asyncio.run(test_zenrows_with_manual_login())
