#!/usr/bin/env python3
"""
Example showing ZenRowsOpenURLResolver with 2Captcha integration.

This demonstrates how to use ZenRows with 2Captcha to handle CAPTCHAs
during redirects to get the final URL.
"""

import os
import asyncio
from scitex.scholar.open_url import ZenRowsOpenURLResolver
from scitex.scholar.auth import AuthenticationManager
from scitex import logging

# Enable debug logging to see what's happening
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

async def main():
    """Main async function to demonstrate ZenRows + 2Captcha."""

    # IMPORTANT: Set your API keys
    # Make sure both are set for CAPTCHA solving to work
    os.environ["SCITEX_SCHOLAR_2CAPTCHA_API_KEY"] = "36d184fbba134f828cdd314f01dc7f18"

    # Verify ZenRows API key is set
    zenrows_key = os.getenv("SCITEX_SCHOLAR_ZENROWS_API_KEY")
    if not zenrows_key:
        print("❌ ERROR: Please set SCITEX_SCHOLAR_ZENROWS_API_KEY environment variable")
        return

    print("✅ 2Captcha API key configured")
    print(f"✅ ZenRows API key configured: {zenrows_key[:8]}...")

    # Initialize authentication manager
    auth_manager = AuthenticationManager(
        email_openathens=os.getenv("SCITEX_SCHOLAR_OPENATHENS_EMAIL")
    )

    # Initialize ZenRows resolver with 2Captcha enabled
    resolver = ZenRowsOpenURLResolver(
        auth_manager,
        os.getenv("SCITEX_SCHOLAR_OPENURL_RESOLVER_URL"),
        zenrows_api_key=zenrows_key,
        enable_captcha_solving=True  # This enables 2Captcha integration
    )

    print("\n🔧 ZenRows resolver initialized with 2Captcha support")

    # Test DOIs including ones that might have CAPTCHAs
    test_dois = [
        "10.1073/pnas.0608765104",  # PNAS - known for anti-bot measures
        "10.1038/nature12373",      # Nature
        "10.1016/j.neuron.2018.01.048",  # Elsevier
        "10.1126/science.1172133",  # Science
        "10.1002/hipo.22488",       # Wiley
    ]

    print("\n📚 Testing DOI resolution with CAPTCHA handling...")
    print("=" * 60)

    for doi in test_dois:
        print(f"\n🔍 Resolving: {doi}")

        try:
            # Resolve with full metadata for better results
            result = await resolver._resolve_single_async(
                doi=doi,
                title="Research Paper",  # Add real title if available
                journal="Journal",       # Add real journal if available
                year=2020               # Add real year if available
            )

            if result:
                print(f"   Success: {result.get('success', False)}")
                print(f"   Final URL: {result.get('final_url', 'None')}")
                print(f"   Access type: {result.get('access_type', 'Unknown')}")

                # Check if CAPTCHA was encountered
                if result.get('final_url') and result.get('success'):
                    print(f"   ✅ Successfully resolved (CAPTCHA handled if present)")
                elif result.get('access_type') == 'zenrows_auth_required':
                    print(f"   ⚠️  Authentication required - browser-based resolver recommended")
                else:
                    print(f"   ❌ No access found")

                if result.get('note'):
                    print(f"   Note: {result['note']}")
            else:
                print(f"   ❌ Resolution failed")

        except Exception as e:
            print(f"   ❌ Error: {e}")

    print("\n" + "=" * 60)
    print("\n📋 Summary:")
    print("- ZenRows with 2Captcha can handle many CAPTCHAs automatically")
    print("- The Zr-Final-Url header tracks redirects through CAPTCHAs")
    print("- Some sites may still require authenticated browser access")
    print("- For best results, use with full metadata (title, journal, year)")

def run_sync_example():
    """Synchronous example using resolve method."""
    print("\n\n=== Synchronous Example ===")

    # Set API keys
    os.environ["SCITEX_SCHOLAR_2CAPTCHA_API_KEY"] = "36d184fbba134f828cdd314f01dc7f18"

    # Initialize
    auth_manager = AuthenticationManager(
        email_openathens=os.getenv("SCITEX_SCHOLAR_OPENATHENS_EMAIL")
    )

    resolver = ZenRowsOpenURLResolver(
        auth_manager,
        os.getenv("SCITEX_SCHOLAR_OPENURL_RESOLVER_URL"),
        os.getenv("SCITEX_SCHOLAR_ZENROWS_API_KEY"),
        enable_captcha_solving=True
    )

    # Resolve synchronously
    doi = "10.1073/pnas.0608765104"
    print(f"\nResolving {doi} synchronously...")

    # Use the resolve method (sync wrapper)
    result = resolver.resolve(doi=doi)
    print(f"Result: {result}")

if __name__ == "__main__":
    # Run async example
    print("🚀 Running async example with 2Captcha...")
    asyncio.run(main())

    # Run sync example
    run_sync_example()

    print("\n\n💡 Tips for using ZenRows with 2Captcha:")
    print("1. Ensure both API keys are set (ZenRows and 2Captcha)")
    print("2. Enable CAPTCHA solving with enable_captcha_solving=True")
    print("3. ZenRows automatically integrates with 2Captcha when configured")
    print("4. The Zr-Final-Url header shows the final destination after CAPTCHAs")
    print("5. For complex authentication flows, consider browser-based resolver")
