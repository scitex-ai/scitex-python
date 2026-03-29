#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-07-31 22:08:31 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex_repo/src/scitex/scholar/browser/remote/_ZenRowsRemoteScholarBrowserManager.py
# ----------------------------------------
from __future__ import annotations

import os

__FILE__ = __file__
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

"""
Browser manager specifically for the ZenRows Scraping Browser service.
This provides cloud-based Chrome instances with built-in anti-bot bypass.
"""
from typing import Any, Dict, Optional

from playwright.async_api import Browser, BrowserContext, Page, async_playwright

from scitex import logging
from scitex_scholar.browser.local.utils._CookieAutoAcceptor import CookieAutoAcceptor

from ._ZenRowsAPIBrowser import ZenRowsAPIBrowser

logger = logging.getLogger(__name__)


class ZenRowsRemoteScholarBrowserManager:
    """
    Manages a connection to the remote ZenRows Scraping Browser service.
    """

    def __init__(
        self,
        auth_manager=None,
        zenrows_api_key: Optional[str] = os.getenv("SCITEX_SCHOLAR_ZENROWS_API_KEY"),
        proxy_country: Optional[str] = os.getenv(
            "SCITEX_SCHOLAR_ZENROWS_PROXY_COUNTRY"
        ),
        **kwargs,
    ):
        """
        Initialize ZenRows browser manager.

        Args:
            auth_manager: Authentication manager for cookie injection.
            zenrows_api_key: ZenRows API key.
            proxy_country: Country code for proxy routing (e.g., 'au', 'us').
                          Note: Country routing may only work with certain endpoints.
            **kwargs: Additional arguments (ignored, for compatibility).
        """
        self.auth_manager = auth_manager
        self.zenrows_api_key = zenrows_api_key
        self.proxy_country = proxy_country
        if not self.zenrows_api_key:
            raise ValueError(
                "ZenRows API key required. Set SCITEX_SCHOLAR_ZENROWS_API_KEY env var "
                "or pass zenrows_api_key parameter"
            )
        self._playwright = None
        self._browser: Optional[Browser] = None
        self._context: Optional[BrowserContext] = None
        self.cookie_acceptor = CookieAutoAcceptor()

        # Also initialize API browser for reliable screenshots
        self._api_browser = ZenRowsAPIBrowser(
            api_key=self.zenrows_api_key, proxy_country=self.proxy_country or "au"
        )

    async def get_browser_async(self) -> Browser:
        """Connect to the ZenRows Scraping Browser."""
        if self._browser and self._browser.is_connected():
            return self._browser

        logger.debug("Connecting to ZenRows Scraping Browser...")
        if not self._playwright:
            self._playwright = await async_playwright().start()

        # Build connection URL with optional country parameter
        connection_url = f"wss://browser.zenrows.com?apikey={self.zenrows_api_key}"

        # Note: Country routing via WebSocket URL is not documented
        # but we can try appending it as a parameter
        if self.proxy_country:
            connection_url += f"&proxy_country={self.proxy_country}"
            logger.debug(f"Requesting proxy country: {self.proxy_country.upper()}")

        try:
            self._browser = await self._playwright.chromium.connect_over_cdp(
                connection_url
            )
            logger.debug("Successfully connected to ZenRows browser")

            # Log a note about country routing
            if self.proxy_country:
                logger.debug(
                    "Note: Country routing via Scraping Browser is experimental. "
                    "Use API mode for guaranteed country-specific IPs."
                )

            return self._browser
        except Exception as e:
            logger.error(f"Failed to connect to ZenRows browser: {e}")
            raise

    async def get_authenticated_browser_and_context_async(
        self,
    ) -> tuple[Browser, BrowserContext]:
        """Get browser context with authentication cookies pre-loaded."""

        if self.auth_manager is None:
            err_msg = (
                "Authentication manager is not set. "
                "Initialize ScholarBrowserManager with an auth_manager to use this method."
            )
            raise ValueError(err_msg)

        browser = await self.get_browser_async()

        if browser.contexts:
            context = browser.contexts[0]
        else:
            context = await browser.new_context()

        # Inject cookie auto-acceptor
        try:
            await self.cookie_acceptor.inject_auto_acceptor_async(context)
            logger.debug("Injected cookie auto-acceptor")
        except Exception as e:
            logger.warn(f"Failed to inject cookie acceptor: {e}")

        if self.auth_manager and await self.auth_manager.is_authenticate_async():
            try:
                cookies = await self.auth_manager.get_auth_cookies_async()
                await context.add_cookies(cookies)
                logger.success(f"Injected {len(cookies)} authentication cookies")
            except Exception as e:
                logger.error(f"Failed to inject auth cookies: {e}")

        self._context = context
        return browser, context

    async def new_page(self, context: Optional[BrowserContext] = None) -> Any:
        """Create a new page in the ZenRows browser."""
        if not context:
            _, context = await self.get_authenticated_browser_and_context_async()

        page = await context.new_page()
        await page.set_extra_http_headers(
            {
                "Accept-Language": "en-US,en;q=0.9",
                "Accept-Encoding": "gzip, deflate, br",
            }
        )
        return page

    async def close(self):
        """Close the ZenRows browser connection."""
        if self._browser and self._browser.is_connected():
            await self._browser.close()
            logger.debug("Closed ZenRows browser connection")
        if self._playwright:
            await self._playwright.stop()
        self._browser = None
        self._context = None
        self._playwright = None

    async def take_screenshot_reliable_async(
        self, url: str, output_path: str, use_api: bool = True, wait_ms: int = 5000
    ) -> Dict[str, Any]:
        """Take a screenshot with automatic CAPTCHA handling.

        This method provides reliable screenshot capture by:
        1. Using the API approach by default (more reliable)
        2. Falling back to WebSocket browser if needed
        3. Automatically handling CAPTCHAs via ZenRows

        Args:
            url: URL to screenshot
            output_path: Path to save screenshot
            use_api: Use API browser (recommended) vs WebSocket
            wait_ms: Additional wait time

        Returns:
            Dict with success status and details
        """
        if use_api:
            # Use API browser for reliability
            logger.debug("Using ZenRows API for screenshot (recommended)")
            return await self._api_browser.navigate_and_screenshot_async(
                url=url, screenshot_path=output_path, wait_ms=wait_ms
            )
        else:
            # Use WebSocket browser (less reliable for captchas)
            logger.debug("Using ZenRows WebSocket browser")
            try:
                browser = await self.get_browser_async()
                context = await browser.new_context()
                page = await context.new_page()

                # Navigate
                await page.goto(url, wait_until="domcontentloaded", timeout=30000)

                # Wait for content
                await page.wait_for_load_state("networkidle", timeout=10000)
                await page.wait_for_timeout(wait_ms)

                # Take screenshot
                await page.screenshot(path=output_path, full_page=True)

                await page.close()
                await context.close()

                return {
                    "success": True,
                    "screenshot": {"saved": True, "path": output_path},
                }
            except Exception as e:
                logger.error(f"WebSocket screenshot failed: {e}")
                return {"success": False, "error": str(e)}

    async def navigate_and_extract_async(
        self,
        url: str,
        extract_pdf_url: bool = True,
        take_screenshot: bool = False,
        screenshot_path: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Navigate to URL and extract information.

        This combines navigation, screenshot, and data extraction.
        Uses the API approach for better reliability.

        Args:
            url: Target URL
            extract_pdf_url: Try to find PDF URL
            take_screenshot: Whether to capture screenshot
            screenshot_path: Where to save screenshot

        Returns:
            Dict with extracted data
        """
        result = await self._api_browser.navigate_and_screenshot_async(
            url=url,
            screenshot_path=screenshot_path if take_screenshot else None,
            return_html=extract_pdf_url,
            wait_ms=8000,  # Longer wait for academic sites
        )

        if extract_pdf_url and result.get("html"):
            # Try to extract PDF URL
            import re

            html = result["html"]

            pdf_patterns = [
                r'href="([^"]+\.pdf[^"]*)"',
                r'content="([^"]+\.pdf[^"]*)"',
                r'data-pdf-url="([^"]+)"',
                r'pdfUrl["\']?\s*:\s*["\']([^"\']+)',
            ]

            for pattern in pdf_patterns:
                match = re.search(pattern, html, re.IGNORECASE)
                if match:
                    result["pdf_url"] = match.group(1)
                    logger.debug(f"Found PDF URL: {result['pdf_url']}")
                    break

        return result

    async def __aenter__(self):
        """Async context manager entry."""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close()


if __name__ == "__main__":
    import asyncio
    import os

    async def main():
        """Comprehensive test of ZenRowsRemoteScholarBrowserManager with comparisons."""
        import json
        from datetime import datetime
        from pathlib import Path

        # Create screenshots directory
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        screenshots_dir = Path(f"./screenshots_remote_{timestamp}")
        screenshots_dir.mkdir(exist_ok=True)

        # Test sites for comprehensive evaluation
        test_sites = [
            ("ip", "https://httpbin.org/ip", "Shows your public IP address"),
            ("headers", "https://httpbin.org/headers", "HTTP headers sent by browser"),
            (
                "bot_detection",
                "https://bot.sannysoft.com/",
                "Bot tests - green=good, red=detected",
            ),
            (
                "fingerprint",
                "https://pixelscan.net/",
                "Browser fingerprinting analysis",
            ),
            ("webrtc", "https://browserleaks.com/webrtc", "WebRTC IP leak test"),
        ]

        async def test_browser_async(browser_type, browser_manager, use_auth=False):
            """Test a browser with all test sites."""
            print(f"\n{'=' * 60}")
            print(f"Testing: {browser_type}")
            print("=" * 60)

            results = {}

            try:
                if use_auth and hasattr(
                    browser_manager, "get_authenticated_browser_and_context_async"
                ):
                    # For managers with auth support
                    (
                        browser,
                        context,
                    ) = (
                        await browser_manager.get_authenticated_browser_and_context_async()
                    )
                    pages_via_context = True
                else:
                    # Direct browser access
                    browser = await browser_manager.get_browser_async()
                    pages_via_context = False

                for test_name, url, description in test_sites:
                    print(f"\n{test_name}: {description}")

                    page = None
                    try:
                        if pages_via_context:
                            page = await context.new_page()
                        else:
                            page = await browser.new_page()

                        # Navigate with timeout
                        await page.goto(
                            url, wait_until="domcontentloaded", timeout=30000
                        )

                        if test_name in ["ip", "headers"]:
                            # Extract text content
                            content = await page.text_content("pre")
                            print(f"Result: {content.strip()[:200]}...")

                            # Parse IP if available
                            if test_name == "ip":
                                try:
                                    ip_data = json.loads(content)
                                    results["ip"] = ip_data.get("origin", "Unknown")
                                    print(f"Detected IP: {results['ip']}")
                                except:
                                    results["ip"] = "Parse error"
                        else:
                            # Wait for dynamic content
                            await page.wait_for_timeout(5000)

                            # For fingerprint test, try to click start button
                            if test_name == "fingerprint":
                                try:
                                    await page.click(
                                        'button:has-text("Start")', timeout=3000
                                    )
                                    await page.wait_for_timeout(5000)
                                except:
                                    pass

                        # Take screenshot
                        screenshot_path = (
                            screenshots_dir
                            / f"{browser_type.lower().replace(' ', '_')}_{test_name}.png"
                        )
                        await page.screenshot(path=screenshot_path, full_page=True)
                        print(f"Screenshot saved: {screenshot_path}")

                        results[test_name] = "Success"

                    except Exception as e:
                        print(f"Failed: {str(e)[:100]}...")
                        results[test_name] = f"Failed: {str(e)[:50]}"
                    finally:
                        if page:
                            await page.close()

                # Clean up
                if hasattr(browser_manager, "close"):
                    await browser_manager.close()

            except Exception as e:
                print(f"Browser initialization failed: {str(e)}")
                results["error"] = str(e)

            return results

        # Store all results
        all_results = {}

        # Test 1: Regular browser (baseline) - if available
        print("\nChecking if we can import local browser for comparison...")
        try:
            from scitex_scholar.browser import ScholarBrowserManager

            print("Initializing regular browser for baseline comparison...")
            regular_manager = ScholarBrowserManager(headless=False)
            regular_results = await test_browser_async(
                "Regular Browser", regular_manager
            )
            all_results["Regular Browser"] = regular_results
        except Exception as e:
            print(f"Regular browser not available for comparison: {e}")
            all_results["Regular Browser"] = {"error": "Not available"}

        # Test 2: ZenRows Remote Browser (default settings)
        print("\nInitializing ZenRows Remote Browser...")
        try:
            zenrows_manager = ZenRowsRemoteScholarBrowserManager()
            zenrows_results = await test_browser_async(
                "ZenRows Remote", zenrows_manager
            )
            all_results["ZenRows Remote"] = zenrows_results
        except Exception as e:
            print(f"ZenRows Remote test failed: {e}")
            all_results["ZenRows Remote"] = {"error": str(e)}

        # Test 3: ZenRows Remote Browser with country (if supported)
        print("\nInitializing ZenRows Remote Browser with AU country...")
        try:
            zenrows_au_manager = ZenRowsRemoteScholarBrowserManager(proxy_country="au")
            zenrows_au_results = await test_browser_async(
                "ZenRows Remote AU", zenrows_au_manager
            )
            all_results["ZenRows Remote AU"] = zenrows_au_results
        except Exception as e:
            print(f"ZenRows Remote AU test failed: {e}")
            all_results["ZenRows Remote AU"] = {"error": str(e)}

        # Test 4: Test the API client as well
        print("\nTesting ZenRows API Client for comparison...")
        try:
            from ._ZenRowsAPIClient import ZenRowsAPIClient

            print("Testing basic API request...")
            api_client = ZenRowsAPIClient()
            response = api_client.request("https://httpbin.org/ip")
            if response.status_code == 200:
                ip_data = json.loads(response.text)
                print(f"API Client IP (Basic): {ip_data.get('origin', 'Unknown')}")
                print(
                    f"API Cost: {response.headers.get('X-Request-Cost', 'Unknown')} credits"
                )
                all_results["API Client Basic"] = {
                    "ip": ip_data.get("origin", "Unknown")
                }

            print("\nTesting API with Australian proxy...")
            api_client_au = ZenRowsAPIClient(default_country="au")
            response_au = api_client_au.request("https://httpbin.org/ip")
            if response_au.status_code == 200:
                ip_data_au = json.loads(response_au.text)
                print(f"API Client IP (AU): {ip_data_au.get('origin', 'Unknown')}")
                print(
                    f"API Cost: {response_au.headers.get('X-Request-Cost', 'Unknown')} credits"
                )
                all_results["API Client AU"] = {
                    "ip": ip_data_au.get("origin", "Unknown")
                }
        except Exception as e:
            print(f"API Client test failed: {e}")
            all_results["API Client"] = {"error": str(e)}

        # Print summary
        print("\n" + "=" * 60)
        print("SUMMARY REPORT")
        print("=" * 60)

        print("\nIP Addresses detected:")
        for method, data in all_results.items():
            if isinstance(data, dict):
                ip = data.get("ip", "Not tested")
            else:
                ip = "Error"
            print(f"  {method:.<35} {ip}")

        print(f"\nScreenshots saved in: {screenshots_dir.absolute()}")

        # Save summary report
        summary_path = screenshots_dir / "test_summary.json"
        with open(summary_path, "w") as f:
            json.dump(
                {
                    "timestamp": timestamp,
                    "results": all_results,
                    "test_sites": [
                        {"name": t[0], "url": t[1], "description": t[2]}
                        for t in test_sites
                    ],
                },
                f,
                indent=2,
            )
        print(f"Summary report saved: {summary_path}")

        # Comparison notes
        print("\n" + "=" * 60)
        print("COMPARISON NOTES:")
        print("=" * 60)
        print("1. Regular Browser: Uses your local IP, no proxy")
        print("2. ZenRows Remote: Cloud browser with built-in anti-bot")
        print("3. ZenRows Remote AU: Attempts Australian IP (experimental)")
        print("4. API Client Basic: Direct API without country routing")
        print("5. API Client AU: Guaranteed Australian IP via API mode")
        print("\nRecommendation: Use API Client for country-specific needs,")
        print("Remote Browser for complex JavaScript sites.")

    # async def main():
    #     """Example usage of ZenRowsRemoteScholarBrowserManager."""
    #     # Get API key from environment or use a test key
    #     api_key = os.getenv(
    #         "SCITEX_SCHOLAR_ZENROWS_API_KEY", "your_api_key_here"
    #     )

    #     # Initialize remote browser manager
    #     async with ZenRowsRemoteScholarBrowserManager(api_key=api_key) as manager:
    #         try:
    #             # Connect to ZenRows Scraping Browser
    #             browser = await manager.connect()
    #             print("Connected to ZenRows Scraping Browser")

    #             # Get the browser context
    #             context = await manager.get_context()

    #             # Create a new page
    #             page = await context.new_page()

    #             # Navigate to a site with anti-bot protection
    #             print("Navigating to protected site...")
    #             await page.goto("https://httpbin.org/headers", wait_until="domcontentloaded", timeout=30000)

    #             # Get page content
    #             content = await page.content()
    #             print("Page loaded successfully")

    #             # Check headers to verify we're using ZenRows
    #             import json

    #             try:
    #                 # Extract JSON from pre tag
    #                 pre_element = await page.query_selector("pre")
    #                 if pre_element:
    #                     text = await pre_element.inner_text()
    #                     headers = json.loads(text)
    #                     print("\nRequest headers seen by server:")
    #                     for key, value in headers.get("headers", {}).items():
    #                         print(f"  {key}: {value}")
    #             except Exception as e:
    #                 print(f"Could not parse headers: {e}")

    #             # Example: Navigate to a site that requires authentication
    #             print("\nNavigating to academic site...")
    #             await page.goto("https://scholar.google.com", wait_until="domcontentloaded", timeout=30000)
    #             await page.wait_for_timeout(2000)

    #             # Take screenshot
    #             await page.screenshot(path="zenrows_remote_screenshot.png")
    #             print("Screenshot saved as zenrows_remote_screenshot.png")

    #             # Example: Handle dynamic content
    #             print("\nTesting dynamic content handling...")
    #             await page.goto("https://example.com", wait_until="domcontentloaded", timeout=30000)
    #             title = await page.title()
    #             print(f"Page title: {title}")

    #         except Exception as e:
    #             print(f"Error during browser operation: {e}")
    #             import traceback

    #             traceback.print_exc()

    #     print("\nZenRows browser session closed")

    # Run the example
    asyncio.run(main())

# python -m scitex.scholar.browser.remote._ZenRowsRemoteScholarBrowserManager

# EOF
