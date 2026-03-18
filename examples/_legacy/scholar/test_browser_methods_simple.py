#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Simplified test focusing on IP detection and bot detection

import asyncio
import json
from pathlib import Path

from scitex.scholar.browser.local import BrowserManager, ZenRowsBrowserManager
from scitex.scholar.browser.remote import ZenRowsRemoteBrowserManager, ZenRowsAPIClient


async def quick_test():
    """Quick test to compare IP addresses across all methods."""

    print("Quick Browser Comparison Test")
    print("="*50)

    # Test regular browser
    print("\n1. Regular Browser:")
    try:
        manager = BrowserManager(headless=True)
        browser = await manager.get_browser()
        page = await browser.new_page()
        await page.goto("http://httpbin.org/ip")
        content = await page.text_content("pre")
        print(f"   IP: {json.loads(content)['origin']}")
        await page.close()
        await manager.close()
    except Exception as e:
        print(f"   Failed: {e}")

    # Test ZenRows Local Proxy
    print("\n2. ZenRows Local Proxy:")
    try:
        manager = ZenRowsBrowserManager(headless=True)
        browser = await manager.get_browser()
        page = await browser.new_page()
        await page.goto("http://httpbin.org/ip")
        content = await page.text_content("pre")
        print(f"   IP: {json.loads(content)['origin']}")
        await page.close()
        await manager.close()
    except Exception as e:
        print(f"   Failed: {e}")

    # Test ZenRows Scraping Browser
    print("\n3. ZenRows Scraping Browser:")
    try:
        manager = ZenRowsRemoteBrowserManager()
        browser = await manager.get_browser()
        page = await browser.new_page()
        await page.goto("http://httpbin.org/ip")
        content = await page.text_content("pre")
        print(f"   IP: {json.loads(content)['origin']}")
        await page.close()
        await manager.close()
    except Exception as e:
        print(f"   Failed: {e}")

    # Test ZenRows API (no country)
    print("\n4. ZenRows API (Basic):")
    try:
        client = ZenRowsAPIClient()
        response = client.request("http://httpbin.org/ip")
        data = json.loads(response.text)
        print(f"   IP: {data['origin']}")
        print(f"   Cost: {response.headers.get('X-Request-Cost', 'Unknown')} credits")
    except Exception as e:
        print(f"   Failed: {e}")

    # Test ZenRows API (Australian)
    print("\n5. ZenRows API (Australia):")
    try:
        client = ZenRowsAPIClient()
        response = client.request("http://httpbin.org/ip", country='au')
        data = json.loads(response.text)
        print(f"   IP: {data['origin']}")
        print(f"   Cost: {response.headers.get('X-Request-Cost', 'Unknown')} credits")
    except Exception as e:
        print(f"   Failed: {e}")

    print("\n" + "="*50)
    print("Test completed!")


if __name__ == "__main__":
    asyncio.run(quick_test())
