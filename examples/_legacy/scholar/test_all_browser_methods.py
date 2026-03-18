#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Comprehensive test of all browser methods including ZenRows options

import asyncio
import json
from pathlib import Path
from datetime import datetime

from scitex.scholar.auth import AuthenticationManager
from scitex.scholar.browser.local import BrowserManager, ZenRowsBrowserManager
from scitex.scholar.browser.remote import ZenRowsRemoteBrowserManager, ZenRowsAPIClient


async def main():
    """Test all browser methods with comprehensive checks."""

    # Initialize auth manager
    auth_manager = AuthenticationManager()
    await auth_manager.authenticate()

    # Create screenshots directory with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    screenshots_dir = Path(f"./screenshots_comparison_{timestamp}")
    screenshots_dir.mkdir(exist_ok=True)

    # Test sites for comprehensive evaluation
    test_sites = [
        ("ip", "https://httpbin.org/ip", "Shows your public IP address"),
        ("headers", "https://httpbin.org/headers", "HTTP headers sent by browser"),
        ("bot_detection", "https://bot.sannysoft.com/", "Bot tests - green=good, red=detected"),
        ("fingerprint", "https://pixelscan.net/", "Browser fingerprinting analysis"),
        ("webrtc", "https://browserleaks.com/webrtc", "WebRTC IP leak test"),
    ]

    # Results summary
    results = {}

    async def test_browser_method(method_name, browser_manager=None, use_api=False):
        """Test a specific browser method."""
        print(f"\n{'='*60}")
        print(f"Testing: {method_name}")
        print('='*60)

        method_results = {}

        if use_api:
            # Special handling for API client
            client = browser_manager
            for test_name, url, description in test_sites:
                print(f"\n{test_name}: {description}")
                try:
                    # API client doesn't support all test sites
                    if test_name in ["ip", "headers"]:
                        # Use HTTP for httpbin to avoid SSL issues
                        test_url = url.replace("https://", "http://") if "httpbin.org" in url else url
                        response = client.request(test_url)

                        if response.status_code == 200:
                            content = response.text
                            print(f"Result: {content.strip()}")

                            # Parse IP if available
                            if test_name == "ip":
                                try:
                                    ip_data = json.loads(content)
                                    method_results['ip'] = ip_data.get('origin', 'Unknown')
                                except:
                                    method_results['ip'] = 'Parse error'

                            # Save response as HTML file instead of screenshot
                            html_path = screenshots_dir / f"{method_name.lower().replace(' ', '_')}_{test_name}.html"
                            html_path.write_text(content)
                            print(f"Response saved: {html_path}")
                        else:
                            print(f"Failed with status: {response.status_code}")
                    else:
                        print("Skipped - API mode doesn't support browser tests")
                except Exception as e:
                    print(f"Failed: {str(e)[:100]}...")
        else:
            # Browser-based methods
            try:
                browser = await browser_manager.get_browser()

                for test_name, url, description in test_sites:
                    page = await browser.new_page()
                    print(f"\n{test_name}: {description}")

                    try:
                        # Use HTTP for httpbin.org to avoid SSL issues with proxy
                        test_url = url.replace("https://", "http://") if "httpbin.org" in url else url

                        # Add response listener for debugging
                        responses = []
                        page.on("response", lambda r: responses.append(r) if r.status >= 400 else None)

                        await page.goto(test_url, timeout=30000, wait_until="domcontentloaded")

                        # Check for failed responses
                        if responses:
                            print(f"Warning: {len(responses)} failed responses detected")

                        if test_name in ["ip", "headers"]:
                            content = await page.text_content("pre")
                            print(f"Result: {content.strip()}")

                            # Parse IP
                            if test_name == "ip":
                                try:
                                    ip_data = json.loads(content)
                                    method_results['ip'] = ip_data.get('origin', 'Unknown')
                                except:
                                    method_results['ip'] = 'Parse error'
                        else:
                            # Wait for dynamic content
                            await page.wait_for_timeout(5000)

                            # For fingerprint test, click the button if available
                            if test_name == "fingerprint":
                                try:
                                    await page.click('button:has-text("Start")', timeout=3000)
                                    await page.wait_for_timeout(5000)
                                except:
                                    pass

                        # Take screenshot
                        screenshot_path = screenshots_dir / f"{method_name.lower().replace(' ', '_')}_{test_name}.png"
                        await page.screenshot(path=screenshot_path, full_page=True)
                        print(f"Screenshot saved: {screenshot_path}")

                    except Exception as e:
                        print(f"Failed: {str(e)[:100]}...")
                        method_results[test_name] = "Failed"
                    finally:
                        await page.close()

                # Clean up browser
                if hasattr(browser_manager, 'close'):
                    await browser_manager.close()

            except Exception as e:
                print(f"Browser initialization failed: {str(e)[:100]}...")
                method_results['error'] = str(e)

        results[method_name] = method_results
        return method_results

    # Test 1: Regular browser (baseline)
    regular_manager = BrowserManager(auth_manager=auth_manager, headless=False)
    await test_browser_method("Regular Browser", regular_manager)

    # Test 2: ZenRows Local Proxy (no country)
    zenrows_local = ZenRowsBrowserManager(auth_manager=auth_manager, headless=False)
    await test_browser_method("ZenRows Local Proxy", zenrows_local)

    # Test 3: ZenRows Remote Browser (Scraping Browser)
    try:
        zenrows_remote = ZenRowsRemoteBrowserManager(auth_manager=auth_manager)
        await test_browser_method("ZenRows Scraping Browser", zenrows_remote)
    except Exception as e:
        print(f"ZenRows Remote Browser failed to initialize: {e}")
        results["ZenRows Scraping Browser"] = {"error": str(e)}

    # Test 4: ZenRows API Client (with Australian IP)
    try:
        zenrows_api = ZenRowsAPIClient(default_country='au')
        await test_browser_method("ZenRows API (AU)", zenrows_api, use_api=True)
    except Exception as e:
        print(f"ZenRows API Client failed: {e}")
        results["ZenRows API (AU)"] = {"error": str(e)}

    # Test 5: ZenRows API Client (no country for comparison)
    try:
        zenrows_api_basic = ZenRowsAPIClient()
        await test_browser_method("ZenRows API (Basic)", zenrows_api_basic, use_api=True)
    except Exception as e:
        print(f"ZenRows API Basic failed: {e}")
        results["ZenRows API (Basic)"] = {"error": str(e)}

    # Print summary
    print("\n" + "="*60)
    print("SUMMARY REPORT")
    print("="*60)

    print("\nIP Addresses detected:")
    for method, data in results.items():
        ip = data.get('ip', 'Not tested')
        print(f"  {method:.<30} {ip}")

    print(f"\nScreenshots and responses saved in: {screenshots_dir.absolute()}")

    # Create summary report
    summary_path = screenshots_dir / "test_summary.json"
    with open(summary_path, 'w') as f:
        json.dump({
            'timestamp': timestamp,
            'results': results,
            'test_sites': test_sites
        }, f, indent=2)
    print(f"Summary report saved: {summary_path}")


if __name__ == "__main__":
    asyncio.run(main())
