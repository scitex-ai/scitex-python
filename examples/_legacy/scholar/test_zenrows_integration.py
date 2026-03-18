#!/usr/bin/env python3
"""
Test ZenRows Scraping Browser integration with OpenURL resolver.

This script verifies that the ZenRows browser backend works correctly
for resolving DOIs through institutional authentication.
"""

import asyncio
import os
from scitex.scholar import ScholarConfig
from scitex.scholar.open_url import OpenURLResolver

async def test_zenrows_resolver():
    """Test OpenURL resolver with ZenRows Scraping Browser."""

    # Ensure environment variables are set
    required_vars = [
        "SCITEX_SCHOLAR_BROWSER_BACKEND",
        "SCITEX_SCHOLAR_ZENROWS_API_KEY",
        "SCITEX_SCHOLAR_2CAPTCHA_API_KEY"
    ]

    for var in required_vars:
        if not os.getenv(var):
            print(f"Error: {var} not set. Please source .env.zenrows first.")
            return

    print("Environment variables verified ✓")
    print(f"Browser backend: {os.getenv('SCITEX_SCHOLAR_BROWSER_BACKEND')}")
    print(f"Proxy country: {os.getenv('SCITEX_SCHOLAR_ZENROWS_PROXY_COUNTRY', 'us')}")

    # Create config with ZenRows backend
    config = ScholarConfig(
        browser_backend="zenrows",
        zenrows_proxy_country="au"
    )

    # Test DOI
    test_doi = "10.1038/s41586-023-06516-4"

    print(f"\nTesting DOI: {test_doi}")
    print("Creating OpenURL resolver with ZenRows backend...")

    async with OpenURLResolver(config=config) as resolver:
        print("Resolver initialized successfully")

        try:
            print("Attempting to resolve DOI...")
            result = await resolver.resolve(test_doi)

            if result.get("pdf_url"):
                print(f"✓ Success! PDF URL found: {result['pdf_url']}")
            else:
                print(f"✗ No PDF URL found. Full result: {result}")

        except Exception as e:
            print(f"✗ Error resolving DOI: {e}")

if __name__ == "__main__":
    print("ZenRows Scraping Browser Integration Test")
    print("=========================================")
    asyncio.run(test_zenrows_resolver())
