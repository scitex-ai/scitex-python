#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-10-18 (ywatanabe)"
# File: ./examples/capture_examples/basic_usage.py
# ----------------------------------------

"""Basic usage examples for scitex.capture module.

This demonstrates the core functionality of the cammy integration.
"""

from scitex import capture
from scitex.logging import getLogger

logger = getLogger(__name__)


def example_single_screenshot():
    """Example: Capture a single screenshot."""
    logger.info("Example 1: Single Screenshot")

    # Basic screenshot
    path = capture.screenshot(message="basic_example")
    logger.success(f"Screenshot saved to: {path}")

    # High-quality screenshot
    path = capture.screenshot(quality=95, message="high_quality")
    logger.success(f"High-quality screenshot saved to: {path}")


def example_app_screenshot():
    """Example: Capture specific application window."""
    logger.info("Example 2: Application Screenshot")

    # Capture Chrome browser
    try:
        path = capture.screenshot(app="chrome", message="browser_state")
        logger.success(f"Chrome screenshot saved to: {path}")
    except Exception as e:
        logger.warning(f"Chrome not found or not running: {e}")

    # Capture VS Code
    try:
        path = capture.screenshot(app="code", message="editor_state")
        logger.success(f"VS Code screenshot saved to: {path}")
    except Exception as e:
        logger.warning(f"VS Code not found or not running: {e}")


def example_monitoring():
    """Example: Continuous monitoring with automatic screenshots."""
    logger.info("Example 3: Continuous Monitoring")

    # Start monitoring
    capture.start_monitoring(interval=2.0, quality=60, verbose=True)
    logger.success("Monitoring started (capturing every 2 seconds)")

    # Get status
    status = capture.get_status()
    logger.info(f"Monitoring active: {status.get('is_monitoring', False)}")
    logger.info(f"Screenshots captured: {status.get('screenshots_captured', 0)}")

    # In a real scenario, you would do work here while monitoring runs
    import time
    logger.info("Working for 10 seconds while monitoring...")
    time.sleep(10)

    # Stop monitoring
    capture.stop_monitoring()
    logger.success("Monitoring stopped")

    # Check final status
    status = capture.get_status()
    logger.info(f"Total screenshots captured: {status.get('screenshots_captured', 0)}")


def example_session_gif():
    """Example: Create GIF from monitoring session."""
    logger.info("Example 4: Create GIF from Session")

    # List available sessions
    sessions = capture.list_sessions(limit=5)
    logger.info(f"Available sessions: {len(sessions)}")

    if sessions:
        # Create GIF from latest session
        gif_path = capture.create_gif(
            session_id="latest",
            duration=0.5,
            optimize=True,
        )
        logger.success(f"GIF created: {gif_path}")
    else:
        logger.warning("No sessions available. Run monitoring first.")


def example_window_capture():
    """Example: Capture specific windows by handle."""
    logger.info("Example 5: Window Capture")

    # List all windows
    windows = capture.list_windows()
    logger.info(f"Found {len(windows)} windows")

    # Show first 3 windows
    for i, window in enumerate(windows[:3]):
        logger.info(f"  {i+1}. {window.get('title', 'Untitled')} (handle: {window.get('handle')})")

    if windows:
        # Capture first window
        handle = windows[0].get('handle')
        path = capture.capture_window(handle, quality=85)
        logger.success(f"Window captured: {path}")


def example_system_info():
    """Example: Get system monitor and window information."""
    logger.info("Example 6: System Information")

    info = capture.get_info()

    # Display monitor information
    monitors = info.get('monitors', [])
    logger.info(f"Monitors: {len(monitors)}")
    for i, monitor in enumerate(monitors):
        logger.info(f"  Monitor {i}: {monitor}")

    # Display window information
    windows = info.get('windows', [])
    logger.info(f"Windows: {len(windows)}")


def example_cache_management():
    """Example: Manage screenshot cache."""
    logger.info("Example 7: Cache Management")

    # List recent screenshots
    recent = capture.list_recent(limit=5, category="all")
    logger.info(f"Recent screenshots: {len(recent)}")
    for path in recent:
        logger.info(f"  - {path}")

    # Clear cache (keep under 1GB)
    result = capture.clear_cache(max_size_gb=1.0)
    logger.success("Cache cleared (kept under 1GB)")


def main():
    """Run all examples."""
    logger.info("Starting scitex.capture examples")
    logger.info("=" * 60)

    # Run examples
    try:
        example_single_screenshot()
        logger.info("-" * 60)

        example_app_screenshot()
        logger.info("-" * 60)

        example_system_info()
        logger.info("-" * 60)

        example_window_capture()
        logger.info("-" * 60)

        example_cache_management()
        logger.info("-" * 60)

        # Note: Monitoring and GIF examples are commented out
        # as they take time and create many screenshots
        # Uncomment to run them:
        # example_monitoring()
        # logger.info("-" * 60)
        # example_session_gif()

    except Exception as e:
        logger.error(f"Example failed: {e}")
        raise

    logger.info("=" * 60)
    logger.success("All examples completed successfully")


if __name__ == "__main__":
    main()

# EOF
