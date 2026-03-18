#!/usr/bin/env python3
"""
Corrected version of the user's ZenRows resolver code.

This shows the proper way to use ZenRowsOpenURLResolver with 2Captcha.
"""

from scitex.scholar.open_url import OpenURLResolver, ZenRowsOpenURLResolver
from scitex.scholar.auth import AuthenticationManager
import os
import asyncio
from scitex import logging

# Enable debug logging
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

# Set 2Captcha API key for CAPTCHA solving
os.environ["SCITEX_SCHOLAR_2CAPTCHA_API_KEY"] = "36d184fbba134f828cdd314f01dc7f18"

# Initialize authentication
auth_manager = AuthenticationManager(
    email_openathens=os.getenv("SCITEX_SCHOLAR_OPENATHENS_EMAIL")
)

# Choose your resolver
# Standard browser-based resolver (for authenticated access)
# resolver = OpenURLResolver(
#     auth_manager,
#     os.getenv("SCITEX_SCHOLAR_OPENURL_RESOLVER_URL")
# )

# OR: ZenRows cloud browser resolver with 2Captcha (for anti-bot bypass)
resolver = ZenRowsOpenURLResolver(
    auth_manager,
    os.getenv("SCITEX_SCHOLAR_OPENURL_RESOLVER_URL"),
    os.getenv("SCITEX_SCHOLAR_ZENROWS_API_KEY"),
    enable_captcha_solving=True  # Enable 2Captcha integration
)

# DOIs to resolve
dois = [
    "10.1002/hipo.22488",
    "10.1038/nature12373",
    "10.1016/j.neuron.2018.01.048",
    "10.1126/science.1172133",
    "10.1073/pnas.0608765104",  # Known anti-bot issues
]

# CORRECTED: Use the resolve method (sync) or resolve_async (async)
# Method 1: Synchronous resolution
print("=== Synchronous Resolution ===")
result = resolver.resolve(doi=dois[0])
print(f"Result: {result}")

# Method 2: Asynchronous resolution with full details
async def resolve_with_details():
    """Resolve DOIs with full result details."""
    print("\n=== Asynchronous Resolution with Details ===")

    for doi in dois:
        print(f"\nResolving: {doi}")

        # Use _resolve_single_async for detailed results
        result = await resolver._resolve_single_async(doi=doi)

        if result:
            print(f"  Success: {result.get('success', False)}")
            print(f"  Final URL: {result.get('final_url', 'Not found')}")
            print(f"  Access type: {result.get('access_type', 'Unknown')}")

            # The Zr-Final-Url header tracks the final destination
            # even through CAPTCHAs and redirects
            if result.get('final_url') != result.get('resolver_url'):
                print(f"  ✅ Followed redirects to final URL")

            if result.get('note'):
                print(f"  Note: {result['note']}")
        else:
            print(f"  ❌ Resolution failed")

# Run async resolution
asyncio.run(resolve_with_details())

print("\n" + "="*60)
print("💡 Key Points:")
print("="*60)
print("1. 2Captcha is integrated via enable_captcha_solving=True")
print("2. ZenRows uses Zr-Final-Url header to track redirects")
print("3. CAPTCHAs are solved automatically when encountered")
print("4. Some sites may still require authenticated browser access")
print("5. Use standard OpenURLResolver for guaranteed authenticated access")
print("="*60)
