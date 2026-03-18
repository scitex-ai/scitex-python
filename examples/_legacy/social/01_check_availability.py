#!/usr/bin/env python3
# Timestamp: 2026-01-22
# File: examples/social/01_check_availability.py

"""Example: Check socialia availability and list available platforms.

This example demonstrates how to check if the social media integration
is available and what platforms are supported.

No credentials required for this example.
"""

import scitex as stx


def main():
    """Check social module availability."""
    print("=== scitex.social Availability Check ===\n")

    # Check if socialia is installed
    print(f"SOCIALIA_AVAILABLE: {stx.social.SOCIALIA_AVAILABLE}")
    print(f"has_socialia(): {stx.social.has_socialia()}")

    if stx.social.SOCIALIA_AVAILABLE:
        print(f"socialia version: {stx.social.__socialia_version__}")

        print("\nAvailable platform clients:")
        platforms = [
            ("Twitter/X", stx.social.Twitter),
            ("LinkedIn", stx.social.LinkedIn),
            ("Reddit", stx.social.Reddit),
            ("YouTube", stx.social.YouTube),
            ("Google Analytics", stx.social.GoogleAnalytics),
        ]

        for name, cls in platforms:
            print(f"  - {name}: {cls.__module__}.{cls.__name__}")

        print("\nEnvironment variable prefix: SCITEX_")
        print("Example: SCITEX_X_CONSUMER_KEY, SCITEX_LINKEDIN_ACCESS_TOKEN")
    else:
        print("\nsocialia is not installed.")
        print("Install with: pip install socialia")

    return 0


if __name__ == "__main__":
    exit(main())

# EOF
