#!/usr/bin/env python3
# Timestamp: 2026-01-22
# File: examples/social/02_twitter_usage.py

"""Example: Twitter/X integration usage.

This example demonstrates how to use the Twitter/X client for posting.

Required environment variables (use SCITEX_ prefix):
- SCITEX_X_CONSUMER_KEY
- SCITEX_X_CONSUMER_SECRET
- SCITEX_X_ACCESS_TOKEN
- SCITEX_X_ACCESS_TOKEN_SECRET

Note: This example only shows the API - actual posting requires valid credentials.
"""

import scitex as stx


def main():
    """Demonstrate Twitter/X client usage."""
    print("=== scitex.social Twitter/X Example ===\n")

    if not stx.social.SOCIALIA_AVAILABLE:
        print("socialia not installed. Install with: pip install socialia")
        return 1

    # Show class info
    print(f"Twitter class: {stx.social.Twitter}")
    print(f"TwitterPoster (alias): {stx.social.TwitterPoster}")

    # Example usage (commented out - requires credentials)
    print("\nExample code:")
    print("""
    import scitex as stx

    # Initialize client (reads SCITEX_X_* env vars)
    x = stx.social.Twitter()

    # Post a tweet
    x.post("Hello from SciTeX! #research #automation")

    # Post with media (if supported)
    # x.post("Check out this figure!", media_path="./figure.png")
    """)

    print("\nRequired environment variables:")
    env_vars = [
        "SCITEX_X_CONSUMER_KEY",
        "SCITEX_X_CONSUMER_SECRET",
        "SCITEX_X_ACCESS_TOKEN",
        "SCITEX_X_ACCESS_TOKEN_SECRET",
    ]
    for var in env_vars:
        print(f"  - {var}")

    return 0


if __name__ == "__main__":
    exit(main())

# EOF
