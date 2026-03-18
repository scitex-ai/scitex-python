#!/usr/bin/env python3
"""
How to access paywalled journals with SciTeX Scholar.

For paywalled content, you MUST use the standard OpenURLResolver (not ZenRows)
because it requires your institutional authentication.
"""

from scitex.scholar.open_url import OpenURLResolver, ZenRowsOpenURLResolver
from scitex.scholar.auth import AuthenticationManager
from scitex.scholar import Scholar
import os
import asyncio
from scitex import logging

# Enable debug logging
logging.basicConfig(level=logging.INFO)

print("="*70)
print("🔐 ACCESSING PAYWALLED JOURNALS WITH SCITEX")
print("="*70)

# Method 1: Using Scholar (RECOMMENDED)
print("\n✅ METHOD 1: Using Scholar (Automatic & Best)")
print("-"*50)

# Scholar automatically handles authentication and resolver selection
scholar = Scholar()

# Ensure you're authenticated
if scholar.config.openathens_enabled:
    print("Checking OpenAthens authentication...")
    is_auth = scholar.is_openathens_authenticated()
    if not is_auth:
        print("🔑 Authenticating with OpenAthens...")
        success = scholar.authenticate_openathens()
        if success:
            print("✅ Authentication successful!")
        else:
            print("❌ Authentication failed - paywalled access won't work")

# Download paywalled papers
paywalled_dois = [
    "10.1038/nature12373",  # Nature (usually paywalled)
    "10.1016/j.cell.2020.05.032",  # Cell (usually paywalled)
    "10.1126/science.abg6155",  # Science (usually paywalled)
]

print("\nDownloading paywalled papers...")
results = scholar.download_pdfs(paywalled_dois)

for paper in results.papers:
    if hasattr(paper, 'pdf_path') and paper.pdf_path:
        print(f"✅ Downloaded: {paper.title[:50]}...")
        print(f"   Method: {getattr(paper, 'pdf_source', 'Unknown')}")
    else:
        print(f"❌ Failed: {paper.doi}")

# Method 2: Using OpenURLResolver directly (for custom workflows)
print("\n\n✅ METHOD 2: Using OpenURLResolver Directly")
print("-"*50)

# Initialize authentication
auth_manager = AuthenticationManager(
    email_openathens=os.getenv("SCITEX_SCHOLAR_OPENATHENS_EMAIL")
)

# IMPORTANT: Use standard OpenURLResolver for paywalled content
# NOT ZenRowsOpenURLResolver!
resolver = OpenURLResolver(
    auth_manager,
    os.getenv("SCITEX_SCHOLAR_OPENURL_RESOLVER_URL")
)

async def resolve_paywalled_papers():
    """Resolve paywalled papers with authentication."""

    # Ensure authenticated
    is_auth = await auth_manager.is_authenticated()
    if not is_auth:
        print("Authenticating...")
        success = await auth_manager.authenticate()
        if not success:
            print("❌ Authentication failed!")
            return

    # Test with a paywalled paper
    doi = "10.1038/nature12373"  # Nature paper

    print(f"\nResolving paywalled DOI: {doi}")
    result = await resolver._resolve_single_async(
        doi=doi,
        title="A mesoscale connectome of the mouse brain",
        journal="Nature",
        year=2014
    )

    if result and result.get('success'):
        print(f"✅ Success! Resolved to: {result.get('final_url')}")
        print(f"   Access type: {result.get('access_type')}")
    else:
        print(f"❌ Failed to resolve")
        print(f"   Reason: {result.get('access_type', 'Unknown')}")

    return result

# Run async resolution
result = asyncio.run(resolve_paywalled_papers())

# Method 3: Why ZenRows doesn't work for paywalled content
print("\n\n❌ METHOD 3: Why ZenRows Fails for Paywalled Content")
print("-"*50)

print("""
ZenRows CANNOT access paywalled content because:

1. 🔒 No Authentication Context
   - ZenRows runs on cloud servers
   - It doesn't have your institutional login cookies
   - Can't access your authenticated session

2. 🌐 Different IP Address
   - You login from your IP
   - ZenRows requests from different IPs
   - Institution rejects mismatched IPs

3. 🍪 Cookie Isolation
   - Your browser cookies stay on your machine
   - ZenRows can't access them (security feature)
   - JavaScript auth checks fail

SOLUTION: For paywalled content, you MUST use:
- Scholar with OpenAthens authentication
- Standard OpenURLResolver (not ZenRows)
- Browser-based download strategies
""")

# Example of what happens with ZenRows (DON'T USE for paywalled!)
print("\n⚠️  Example: ZenRows fails on paywalled content")
zenrows_resolver = ZenRowsOpenURLResolver(
    auth_manager,
    os.getenv("SCITEX_SCHOLAR_OPENURL_RESOLVER_URL"),
    os.getenv("SCITEX_SCHOLAR_ZENROWS_API_KEY")
)

# This will fail for paywalled content!
async def test_zenrows_failure():
    result = await zenrows_resolver._resolve_single_async(
        doi="10.1038/nature12373"
    )
    print(f"ZenRows result: {result.get('access_type')}")
    print("Expected: 'zenrows_auth_required' (cannot access)")

asyncio.run(test_zenrows_failure())

print("\n" + "="*70)
print("📚 SUMMARY: Accessing Paywalled Journals")
print("="*70)
print("✅ DO: Use Scholar with authentication (automatic)")
print("✅ DO: Use standard OpenURLResolver for custom workflows")
print("✅ DO: Ensure you're authenticated before downloading")
print("❌ DON'T: Use ZenRowsOpenURLResolver for paywalled content")
print("❌ DON'T: Expect cloud services to access your subscriptions")
print("="*70)
