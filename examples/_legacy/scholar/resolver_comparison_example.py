#!/usr/bin/env python3
"""
Example comparing OpenURLResolver vs OpenURLResolverWithZenRows.

This example demonstrates when to use each resolver based on your needs.
"""

import asyncio
import os
from scitex import logging
from scitex.scholar.auth import AuthenticationManager
from scitex.scholar.open_url import OpenURLResolver, OpenURLResolverWithZenRows

logger = logging.getLogger(__name__)


async def compare_resolvers():
    """Compare the two resolver implementations."""

    # Initialize authentication
    auth_manager = AuthenticationManager(
        email_openathens=os.getenv("SCITEX_SCHOLAR_OPENATHENS_EMAIL")
    )

    resolver_url = os.getenv("SCITEX_SCHOLAR_OPENURL_RESOLVER_URL")

    # Test DOIs - mix of open and paywalled
    test_dois = {
        "10.1371/journal.pone.0001234": "Open Access (PLOS)",
        "10.1038/nature12373": "Paywalled (Nature)",
        "10.1126/science.1234567": "Paywalled (Science)",
    }

    print("OpenURL Resolver Comparison")
    print("=" * 60)

    # Test 1: ZenRows Resolver (fast, good for open access)
    print("\n1. Testing ZenRows Resolver (Anti-bot bypass)")
    print("-" * 40)

    zenrows_resolver = OpenURLResolverWithZenRows(
        auth_manager,
        resolver_url,
        os.getenv("SCITEX_SCHOLAR_ZENROWS_API_KEY")
    )

    for doi, description in test_dois.items():
        print(f"\n{description} - {doi}")
        result = await zenrows_resolver._resolve_single_async(doi=doi)

        if result:
            print(f"  Success: {result['success']}")
            print(f"  URL: {result.get('final_url', 'N/A')}")
            if result.get('suggestion'):
                print(f"  Note: {result['suggestion']}")
        else:
            print("  Failed to resolve")

    # Test 2: Browser Resolver (slower, handles authentication)
    print("\n\n2. Testing Browser Resolver (Full authentication)")
    print("-" * 40)
    print("Note: This requires authenticated session via OpenAthens")

    # Check if authenticated
    if await auth_manager.is_authenticated():
        print("✓ Already authenticated")
    else:
        print("⚠ Not authenticated - would need to login first")
        print("  Run: await auth_manager.authenticate()")

    browser_resolver = OpenURLResolver(auth_manager, resolver_url)

    # Example of browser-based resolution (commented out to avoid browser popup)
    # for doi, description in test_dois.items():
    #     print(f"\n{description} - {doi}")
    #     result = await browser_resolver._resolve_single_async(doi=doi)
    #     if result:
    #         print(f"  Success: {result['success']}")
    #         print(f"  URL: {result.get('final_url', 'N/A')}")

    print("\n\nRecommendations:")
    print("=" * 60)
    print("Use ZenRows Resolver when:")
    print("  - Checking if content is open access")
    print("  - Need to bypass anti-bot detection")
    print("  - Processing many URLs quickly")
    print("  - Don't need authenticated access")
    print("\nUse Browser Resolver when:")
    print("  - Need access to paywalled content")
    print("  - Have institutional authentication")
    print("  - Quality over speed")
    print("  - Following complex authentication flows")


async def main():
    """Run the comparison."""
    try:
        await compare_resolvers()
    except Exception as e:
        logger.error(f"Error: {e}")


if __name__ == "__main__":
    # Set up logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(message)s'
    )

    asyncio.run(main())
