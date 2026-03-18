#!/usr/bin/env python3
"""
Simple SSO Automator Example

This demonstrates how SSO automation should work as part of the authentication
system, not tied to OpenURL resolution.
"""

import asyncio
import os
from playwright.async_api import async_playwright

# This would normally be imported from scitex.scholar.auth.sso_automations
from scitex.scholar.auth.sso_automations import UniversityOfMelbourneSSOAutomator
from scitex.scholar.auth import AuthenticationManager


async def simple_sso_login():
    """Simple example of using SSO automator for authentication."""

    # Create SSO automator
    sso_automator = UniversityOfMelbourneSSOAutomator(
        headless=False,  # Show browser so you can see what's happening
        persistent_session=True  # Save session for reuse
    )

    # Check if we have credentials
    if not sso_automator.has_valid_credentials():
        print("Please set environment variables:")
        print("  export UNIMELB_USERNAME='your-username'")
        print("  export UNIMELB_PASSWORD='your-password'")
        return

    # Check if we already have a valid session
    if sso_automator.is_session_valid():
        print("✓ Already have a valid session!")
        return

    print("Starting SSO login...")

    # Use playwright to create browser
    async with async_playwright() as p:
        # Get browser context (with persistent session if enabled)
        context = await sso_automator.get_browser_context(p)
        page = await context.new_page()

        # Navigate to a protected resource (e.g., library database)
        protected_url = "https://www.nature.com/articles/nature12373"
        print(f"Navigating to: {protected_url}")
        await page.goto(protected_url)

        # Wait a bit to see if we get redirected to SSO
        await page.wait_for_timeout(3000)

        # Check if we're on an SSO page
        if sso_automator.is_sso_page(page.url):
            print("Redirected to SSO login page")

            # Perform automated login
            success = await sso_automator.perform_login(page)

            if success:
                print("✓ SSO login successful!")

                # Wait for redirect back to content
                await page.wait_for_load_state("networkidle")
                print(f"Final URL: {page.url}")

                # Save session info
                sso_automator.save_session_info()
            else:
                print("✗ SSO login failed")
        else:
            print("No SSO redirect - might already be authenticated or no access")

        # Keep browser open for a bit so you can see the result
        await page.wait_for_timeout(5000)

        await context.close()


async def integrated_auth_example():
    """Example showing how SSO should integrate with AuthenticationManager."""

    # Initialize authentication manager
    auth_manager = AuthenticationManager()

    # Register SSO automator with auth manager
    # (This is what should happen - auth manager should know about SSO)
    sso_automator = UniversityOfMelbourneSSOAutomator()

    # In a real implementation, auth_manager would:
    # 1. Check if SSO is needed for the resource
    # 2. Use the appropriate SSO automator
    # 3. Handle the authentication flow
    # 4. Return authenticated browser context

    # For now, let's just show the concept
    print("AuthenticationManager should handle:")
    print("1. OpenAthens authentication")
    print("2. SSO automation (via registered automators)")
    print("3. API key authentication")
    print("4. Cookie/session management")
    print("\nSSO automators should be registered with auth manager, not OpenURL resolver")


def main():
    """Run examples."""
    print("=== Simple SSO Login Example ===")
    asyncio.run(simple_sso_login())

    print("\n=== Integrated Authentication Example ===")
    asyncio.run(integrated_auth_example())


if __name__ == "__main__":
    main()
