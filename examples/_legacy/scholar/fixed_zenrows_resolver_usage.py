#!/usr/bin/env python3
"""
Fixed example for using ZenRowsOpenURLResolver correctly.
"""

from scitex.scholar.open_url import OpenURLResolver, ZenRowsOpenURLResolver
from scitex.scholar.auth import AuthenticationManager
import os
import asyncio
from scitex import logging

# Enable debug logging
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

# Initialize authentication
auth_manager = AuthenticationManager(
    email_openathens=os.getenv("SCITEX_SCHOLAR_OPENATHENS_EMAIL")
)

# Choose your resolver
# # Standard browser-based resolver
# resolver = OpenURLResolver(
#     auth_manager,
#     os.getenv("SCITEX_SCHOLAR_OPENURL_RESOLVER_URL")
# )

# OR: ZenRows cloud browser resolver (for anti-bot bypass)
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

# FIXED: Proper synchronous usage
print("=== Method 1: Resolve single DOI (sync) ===")
# The resolve method expects DOI as first positional argument
result = resolver.resolve(dois[0])
print(f"Result: {result}")

# FIXED: Resolve multiple DOIs (one by one)
print("\n=== Method 2: Resolve multiple DOIs (sync) ===")
results = []
for doi in dois[:3]:  # Test first 3
    print(f"\nResolving: {doi}")
    result = resolver.resolve(doi)
    results.append(result)
    print(f"  Result: {result}")

# FIXED: Async usage for better performance
async def resolve_async_example():
    """Proper async usage with detailed results."""
    print("\n=== Method 3: Async resolution ===")

    # Single DOI async
    result = await resolver._resolve_single_async(doi=dois[0])
    print(f"\nSingle async result:")
    print(f"  Success: {result.get('success', False)}")
    print(f"  Final URL: {result.get('final_url', 'None')}")
    print(f"  Access type: {result.get('access_type', 'Unknown')}")

    # Multiple DOIs in parallel
    print("\n=== Parallel async resolution ===")
    tasks = [resolver._resolve_single_async(doi=doi) for doi in dois[:3]]
    results = await asyncio.gather(*tasks)

    for doi, result in zip(dois[:3], results):
        print(f"\nDOI: {doi}")
        print(f"  Success: {result.get('success', False)}")
        print(f"  Final URL: {result.get('final_url', 'None')}")
        print(f"  Access type: {result.get('access_type', 'Unknown')}")

# Run async example
asyncio.run(resolve_async_example())

print("\n" + "="*60)
print("✅ Fixed usage patterns:")
print("1. Use resolve(doi) for single DOI (sync)")
print("2. Loop through DOIs for multiple (sync)")
print("3. Use _resolve_single_async() for async operations")
print("4. Use asyncio.gather() for parallel resolution")
print("="*60)
