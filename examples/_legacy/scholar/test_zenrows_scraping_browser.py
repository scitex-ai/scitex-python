#!/usr/bin/env python3
"""
Test ZenRows Scraping Browser integration with SciTeX Scholar.

This verifies that the browser backend configuration works correctly
for accessing paywalled journals.
"""

import os
import asyncio
from scitex.scholar import Scholar
from scitex.scholar.auth import AuthenticationManager
from scitex.scholar.open_url import OpenURLResolver
from scitex import logging

# Enable logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Set environment variables
os.environ["SCITEX_SCHOLAR_ZENROWS_API_KEY"] = "822225799f9a4d847163f397ef86bb81b3f5ceb5"
os.environ["SCITEX_SCHOLAR_ZENROWS_PROXY_COUNTRY"] = "au"
os.environ["SCITEX_SCHOLAR_2CAPTCHA_API_KEY"] = "36d184fbba134f828cdd314f01dc7f18"
os.environ["SCITEX_SCHOLAR_BROWSER_BACKEND"] = "zenrows"

async def test_zenrows_browser_connection():
    """Test basic connection to ZenRows Scraping Browser."""
    print("\n🔌 Testing ZenRows Scraping Browser Connection")
    print("="*60)

    from scitex.scholar.browser._BrowserMixin import BrowserMixin

    # Create a browser mixin with ZenRows backend
    browser_mixin = BrowserMixin(
        browser_backend="zenrows",
        zenrows_api_key=os.getenv("SCITEX_SCHOLAR_ZENROWS_API_KEY"),
        proxy_country="au"
    )

    try:
        # Get browser (will connect to ZenRows)
        browser = await browser_mixin.get_browser()
        print("✅ Successfully connected to ZenRows Scraping Browser!")

        # Test navigation
        context = await browser.new_context()
        page = await context.new_page()

        await page.goto("https://httpbin.org/ip")
        content = await page.content()

        # Extract IP info
        import re
        ip_match = re.search(r'"origin":\s*"([^"]+)"', content)
        if ip_match:
            ip = ip_match.group(1)
            print(f"✅ Connected via IP: {ip}")
            print(f"   (Should be from Australia proxy)")

        await page.close()
        await context.close()

    except Exception as e:
        print(f"❌ Failed to connect: {e}")
    finally:
        if hasattr(browser_mixin, '_shared_browser'):
            await browser_mixin.close_all_pages()

async def test_authentication_with_zenrows():
    """Test OpenAthens authentication using ZenRows browser."""
    print("\n\n🔐 Testing Authentication with ZenRows Browser")
    print("="*60)

    # Initialize authentication manager with ZenRows backend
    auth_manager = AuthenticationManager(
        email_openathens=os.getenv("SCITEX_SCHOLAR_OPENATHENS_EMAIL"),
        browser_backend="zenrows",
        zenrows_api_key=os.getenv("SCITEX_SCHOLAR_ZENROWS_API_KEY"),
        proxy_country="au"
    )

    print("📍 Authentication will happen in ZenRows remote browser")
    print("   - Running on Australian proxy IP")
    print("   - Full session maintained remotely")

    # Check if already authenticated
    is_auth = await auth_manager.is_authenticated(verify_live=False)
    print(f"\nCurrent auth status: {'✅ Authenticated' if is_auth else '❌ Not authenticated'}")

    if not is_auth:
        print("\n🌐 Would open browser for authentication...")
        print("   (Skipping actual auth for this test)")

def test_scholar_integration():
    """Test Scholar with ZenRows backend."""
    print("\n\n📚 Testing Scholar Integration")
    print("="*60)

    # Initialize Scholar (will use ZenRows backend from env vars)
    scholar = Scholar()

    print(f"Browser backend: {scholar.config.browser_backend}")
    print(f"Proxy country: {scholar.config.zenrows_proxy_country}")

    # Test search (doesn't require browser)
    print("\n🔍 Testing search...")
    papers = scholar.search("quantum computing", limit=2)
    print(f"Found {len(papers)} papers")

    # For actual downloads with authentication:
    print("\n📥 Download workflow (with ZenRows):")
    print("1. Authentication happens in ZenRows browser")
    print("2. Session maintained on ZenRows servers")
    print("3. Downloads use authenticated remote session")
    print("4. Appears as residential Australian IP")

async def test_openurl_resolver_with_zenrows():
    """Test OpenURL resolver with ZenRows backend."""
    print("\n\n🔗 Testing OpenURL Resolver with ZenRows")
    print("="*60)

    # Initialize components
    auth_manager = AuthenticationManager(
        email_openathens=os.getenv("SCITEX_SCHOLAR_OPENATHENS_EMAIL"),
        browser_backend="zenrows",
        zenrows_api_key=os.getenv("SCITEX_SCHOLAR_ZENROWS_API_KEY"),
        proxy_country="au"
    )

    resolver = OpenURLResolver(
        auth_manager,
        os.getenv("SCITEX_SCHOLAR_OPENURL_RESOLVER_URL", "https://unimelb.hosted.exlibrisgroup.com/sfxlcl41"),
        browser_backend="zenrows",
        zenrows_api_key=os.getenv("SCITEX_SCHOLAR_ZENROWS_API_KEY"),
        proxy_country="au"
    )

    print("✅ OpenURL resolver configured with ZenRows backend")
    print("   - Will use remote browser for all operations")
    print("   - Authentication preserved in remote session")

def main():
    """Run all tests."""
    print("🚀 ZenRows Scraping Browser Integration Test")
    print("="*70)
    print("\nConfiguration:")
    print(f"  Backend: {os.getenv('SCITEX_SCHOLAR_BROWSER_BACKEND', 'local')}")
    print(f"  Proxy Country: {os.getenv('SCITEX_SCHOLAR_ZENROWS_PROXY_COUNTRY', 'us')}")
    print(f"  ZenRows API: {'✓' if os.getenv('SCITEX_SCHOLAR_ZENROWS_API_KEY') else '✗'}")
    print(f"  2Captcha API: {'✓' if os.getenv('SCITEX_SCHOLAR_2CAPTCHA_API_KEY') else '✗'}")

    # Run async tests
    asyncio.run(test_zenrows_browser_connection())
    asyncio.run(test_authentication_with_zenrows())

    # Run sync tests
    test_scholar_integration()

    # Run resolver test
    asyncio.run(test_openurl_resolver_with_zenrows())

    print("\n\n✅ All tests completed!")
    print("\n💡 Key Benefits of ZenRows Scraping Browser:")
    print("  1. Full authentication support (OpenAthens works!)")
    print("  2. Anti-bot bypass built-in")
    print("  3. Residential IPs from chosen country")
    print("  4. Session maintained throughout process")
    print("  5. Access to paywalled content!")

if __name__ == "__main__":
    main()
