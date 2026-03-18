#!/usr/bin/env python3
"""
Comprehensive example of using ZenRows Scraping Browser with SciTeX Scholar.

This example demonstrates:
1. Setting up ZenRows browser backend
2. Authenticating through institutional login
3. Resolving DOIs to full-text PDFs
4. Downloading papers through paywalls
"""

import asyncio
import os
from pathlib import Path
from scitex.scholar import Scholar, ScholarConfig, Papers

async def main():
    """Demonstrate ZenRows integration for accessing paywalled content."""

    # 1. Configuration
    print("1. Setting up ZenRows Scraping Browser configuration...")

    config = ScholarConfig(
        # Use ZenRows remote browser instead of local
        browser_backend="zenrows",

        # Set proxy location (optional, defaults to 'us')
        zenrows_proxy_country="au",

        # Your institutional resolver URL
        resolver_url="https://go.openathens.net/redirector/unisa.edu.au",

        # Authentication credentials (from environment or direct)
        openathens_username=os.getenv("SCITEX_SCHOLAR_OPENATHENS_USERNAME"),
        openathens_password=os.getenv("SCITEX_SCHOLAR_OPENATHENS_PASSWORD"),

        # Enable verbose logging to see what's happening
        verbose=True
    )

    print(f"   Browser backend: {config.browser_backend}")
    print(f"   Proxy country: {config.zenrows_proxy_country}")
    print(f"   Resolver URL: {config.resolver_url}")

    # 2. Create Scholar instance
    print("\n2. Creating Scholar instance with ZenRows backend...")
    scholar = Scholar(config=config)

    # 3. Test with some DOIs
    test_dois = [
        "10.1038/s41586-023-06516-4",  # Nature paper
        "10.1126/science.abj8754",      # Science paper
        "10.1016/j.cell.2023.02.027",   # Cell paper
    ]

    print("\n3. Testing DOI resolution through authenticated access...")

    for doi in test_dois:
        print(f"\n   Resolving {doi}...")
        try:
            # Search for the paper
            papers = await scholar.search(doi)

            if papers:
                paper = papers[0]
                print(f"   ✓ Found: {paper.title}")

                # Try to get PDF URL through institutional access
                if paper.pdf_url:
                    print(f"   ✓ PDF URL: {paper.pdf_url}")
                else:
                    print("   ✗ No PDF URL found")

                # Optionally download the PDF
                # pdf_path = await paper.download_pdf(Path("./pdfs"))
                # if pdf_path:
                #     print(f"   ✓ Downloaded to: {pdf_path}")

            else:
                print(f"   ✗ Paper not found")

        except Exception as e:
            print(f"   ✗ Error: {e}")

    # 4. Batch processing example
    print("\n4. Batch processing multiple papers...")

    papers = Papers()
    for doi in test_dois:
        papers.append({"doi": doi})

    # Enhance all papers with metadata and PDF URLs
    await papers.enhance_metadata_async(
        scholar=scholar,
        include_pdf_urls=True,
        max_concurrent=3  # Process 3 papers concurrently
    )

    print(f"\n   Enhanced {len(papers)} papers:")
    for paper in papers:
        status = "✓" if paper.get("pdf_url") else "✗"
        print(f"   {status} {paper.get('title', 'Unknown')[:60]}...")

    # 5. Advanced usage with custom authentication
    print("\n5. Using custom authentication flow...")

    # You can also manually control the authentication
    from scitex.scholar.auth import AuthenticationManager
    from scitex.scholar.browser import BrowserManager

    # Create browser manager with ZenRows
    browser_manager = BrowserManager(
        config=config,
        browser_backend="zenrows",
        zenrows_proxy_country="au"
    )

    async with browser_manager as bm:
        # Get authenticated browser
        browser = await bm.get_authenticated_browser()

        # Now you can use this browser for custom workflows
        page = await browser.new_page()
        await page.goto("https://scholar.google.com")
        print("   ✓ Successfully connected to Google Scholar via ZenRows")

        await page.close()

    print("\n✓ ZenRows integration test completed!")

if __name__ == "__main__":
    print("ZenRows Scraping Browser Example")
    print("================================")
    print("\nEnsure you have set the following environment variables:")
    print("- SCITEX_SCHOLAR_BROWSER_BACKEND=zenrows")
    print("- SCITEX_SCHOLAR_ZENROWS_API_KEY=your_api_key")
    print("- SCITEX_SCHOLAR_2CAPTCHA_API_KEY=your_2captcha_key")
    print("- SCITEX_SCHOLAR_OPENATHENS_USERNAME=your_username")
    print("- SCITEX_SCHOLAR_OPENATHENS_PASSWORD=your_password")
    print("\nOr source the .env.zenrows file: source .env.zenrows\n")

    asyncio.run(main())
