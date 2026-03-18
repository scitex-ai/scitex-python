#!/usr/bin/env python3
"""
Corrected example for using ZenRowsOpenURLResolver.

Based on the user's code but with proper method calls.
"""

from scitex.scholar.open_url import OpenURLResolver, ZenRowsOpenURLResolver
from scitex.scholar.auth import AuthenticationManager
import os
from scitex import logging
import asyncio

# Enable debug logging
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

# Initialize authentication
auth_manager = AuthenticationManager(
    email_openathens=os.getenv("SCITEX_SCHOLAR_OPENATHENS_EMAIL")
)

# Choose your resolver
# Standard browser-based resolver (RECOMMENDED for authenticated access)
# resolver = OpenURLResolver(
#     auth_manager,
#     os.getenv("SCITEX_SCHOLAR_OPENURL_RESOLVER_URL")
# )

# OR: ZenRows cloud browser resolver (for anti-bot bypass)
# NOTE: ZenRows has limitations with JavaScript redirects that require authentication
resolver = ZenRowsOpenURLResolver(
    auth_manager,
    os.getenv("SCITEX_SCHOLAR_OPENURL_RESOLVER_URL"),
    os.getenv("SCITEX_SCHOLAR_ZENROWS_API_KEY")
)

# DOIs to resolve
dois = [
    "10.1002/hipo.22488",
    "10.1038/nature12373",
    "10.1016/j.neuron.2018.01.048",
    "10.1126/science.1172133",
    "10.1073/pnas.0608765104",  # Known anti-bot issues
]

# Method 1: Use the sync wrapper (resolve_doi_sync)
print("=== Method 1: Sync Resolution ===")
result = resolver.resolve_doi_sync(doi=dois[0])
print(f"Result: {result}")

# Method 2: Use async resolution
async def resolve_async():
    """Async resolution example."""
    print("\n=== Method 2: Async Resolution ===")

    # Resolve single DOI
    result = await resolver._resolve_single_async(doi=dois[0])
    print(f"Single result: {result}")

    # Resolve multiple DOIs
    print("\n=== Resolving multiple DOIs ===")
    tasks = [resolver._resolve_single_async(doi=doi) for doi in dois]
    results = await asyncio.gather(*tasks)

    for doi, result in zip(dois, results):
        print(f"\nDOI: {doi}")
        print(f"  Success: {result.get('success', False)}")
        print(f"  Final URL: {result.get('final_url', 'None')}")
        print(f"  Access type: {result.get('access_type', 'Unknown')}")
        if result.get('note'):
            print(f"  Note: {result['note']}")

# Run async resolution
asyncio.run(resolve_async())

# Method 3: Use the high-level resolve_async method
async def resolve_high_level():
    """High-level async resolution."""
    print("\n=== Method 3: High-level Resolution ===")

    # This method includes retry logic and better error handling
    result = await resolver.resolve_async(doi=dois[0])
    print(f"High-level result: {result}")

asyncio.run(resolve_high_level())

# Important notes about ZenRows limitations
print("\n" + "="*60)
print("⚠️  IMPORTANT NOTES ABOUT ZENROWS:")
print("="*60)
print("1. ZenRows cannot follow JavaScript redirects that require authentication")
print("2. It may stay at the institutional resolver page")
print("3. For authenticated access, use the standard OpenURLResolver instead")
print("4. ZenRows is better for discovering which papers have access")
print("5. Use it for high-volume processing where some failures are acceptable")
print("="*60)
