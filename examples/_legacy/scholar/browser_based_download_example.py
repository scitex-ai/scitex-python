#!/usr/bin/env python3
"""
Example of browser-based PDF downloads with OpenAthens.

This approach keeps the browser session alive and downloads PDFs
by navigating within the authenticated session, avoiding cookie
domain issues entirely.
"""

import asyncio
from pathlib import Path
from scitex.scholar import BrowserBasedDownloader, MinimalOpenAthensAuthenticator


async def download_with_browser():
    """Example of browser-based downloads."""

    print("🌐 Browser-Based PDF Download Example")
    print("="*60)

    # Create downloader
    downloader = BrowserBasedDownloader(headless=False)

    # Step 1: Authenticate with OpenAthens
    print("\n1️⃣ Authenticating with OpenAthens...")
    success = await downloader.authenticate_openathens(
        email="user@university.edu"  # Replace with your email
    )

    if not success:
        print("❌ Authentication failed")
        return

    # Step 2: Download papers
    print("\n2️⃣ Downloading papers...")

    # Example papers (replace with your DOIs)
    paper_urls = [
        "https://doi.org/10.1038/s41586-021-03819-2",  # Nature paper
        "https://doi.org/10.1126/science.abe9868",      # Science paper
        "https://doi.org/10.1016/j.cell.2021.01.007",  # Cell paper
    ]

    # Download directory
    download_dir = Path("./downloads")

    # Download papers
    results = await downloader.download_papers(
        paper_urls,
        download_dir
    )

    # Step 3: Show results
    print(f"\n3️⃣ Results Summary:")
    print(f"   ✅ Successful: {results['success']}")
    print(f"   ❌ Failed: {results['failed']}")
    print(f"   📁 Download directory: {download_dir.absolute()}")

    # Close browser
    await downloader.close()

    print("\n✨ Done!")


async def minimal_authentication_example():
    """Example of minimal OpenAthens authentication."""

    print("\n🔐 Minimal Authentication Example")
    print("="*60)

    # Create authenticator
    auth = MinimalOpenAthensAuthenticator(
        email="user@university.edu"
    )

    # Check if already authenticated
    if await auth.is_authenticated():
        print("✅ Using cached authentication")
        cookies = await auth.get_cookies()
        print(f"   Found {len(cookies)} cookies")
    else:
        print("🔐 Need to authenticate")
        success = await auth.authenticate()

        if success:
            print("✅ Authentication successful")
            cookies = await auth.get_cookies()
            print(f"   Saved {len(cookies)} cookies")
        else:
            print("❌ Authentication failed")


async def main():
    """Run examples."""

    print("SciTeX Scholar - Browser-Based Download Examples")
    print("="*60)
    print("\nThis example demonstrates:")
    print("1. Minimal OpenAthens authentication (reduced automation)")
    print("2. Browser-based PDF downloads (no cookie domain issues)")
    print("\n")

    # Choose which example to run
    print("Which example would you like to run?")
    print("1. Browser-based downloads (recommended)")
    print("2. Minimal authentication only")
    print("3. Both examples")

    choice = input("\nEnter choice (1-3): ").strip()

    if choice == "1":
        await download_with_browser()
    elif choice == "2":
        await minimal_authentication_example()
    elif choice == "3":
        await minimal_authentication_example()
        print("\n" + "-"*60 + "\n")
        await download_with_browser()
    else:
        print("Invalid choice")


if __name__ == "__main__":
    asyncio.run(main())
