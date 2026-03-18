#!/usr/bin/env python3
# Timestamp: 2026-01-22
# File: examples/social/03_youtube_analytics.py

"""Example: YouTube Analytics integration.

This example demonstrates how to use the YouTube client for analytics.

Required environment variables (use SCITEX_ prefix):
- SCITEX_YOUTUBE_API_KEY

Note: This example only shows the API - actual usage requires valid credentials.
"""

import scitex as stx


def main():
    """Demonstrate YouTube analytics usage."""
    print("=== scitex.social YouTube Analytics Example ===\n")

    if not stx.social.SOCIALIA_AVAILABLE:
        print("socialia not installed. Install with: pip install socialia")
        return 1

    # Show class info
    print(f"YouTube class: {stx.social.YouTube}")

    # Example usage (commented out - requires credentials)
    print("\nExample code:")
    print("""
    import scitex as stx

    # Initialize client (reads SCITEX_YOUTUBE_* env vars)
    yt = stx.social.YouTube()

    # Get channel statistics
    stats = yt.get_channel_stats()
    print(f"Subscribers: {stats['subscriberCount']}")
    print(f"Total views: {stats['viewCount']}")
    print(f"Video count: {stats['videoCount']}")

    # Get video analytics
    video_stats = yt.get_video_stats("VIDEO_ID")
    """)

    print("\nRequired environment variables:")
    print("  - SCITEX_YOUTUBE_API_KEY")

    return 0


if __name__ == "__main__":
    exit(main())

# EOF
