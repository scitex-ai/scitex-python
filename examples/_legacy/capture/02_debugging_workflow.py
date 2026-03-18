#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-10-18 (ywatanabe)"
# File: ./examples/capture_examples/debugging_workflow.py
# ----------------------------------------

"""Example: Using scitex.capture for debugging workflows.

This demonstrates how to use screen capture to document and debug
long-running processes, especially useful for browser automation
and GUI testing.
"""

import time
from scitex import capture
from scitex.logging import getLogger

logger = getLogger(__name__)


def simulate_browser_automation():
    """Simulate a browser automation workflow with screenshots."""
    logger.info("Starting browser automation simulation")

    # Take initial screenshot
    capture.screenshot(message="start_automation")
    logger.info("Initial state captured")

    # Simulate various steps
    steps = [
        "navigate_to_page",
        "fill_form",
        "submit_data",
        "wait_for_response",
        "verify_results",
    ]

    for i, step in enumerate(steps):
        logger.info(f"Step {i+1}/{len(steps)}: {step}")
        time.sleep(0.5)  # Simulate work

        # Capture screenshot at each step
        path = capture.screenshot(message=f"step_{i+1}_{step}")
        logger.success(f"Screenshot captured: {path}")

    logger.success("Browser automation completed")


def monitor_long_running_process():
    """Monitor a long-running process with continuous screenshots."""
    logger.info("Starting long-running process monitoring")

    # Start monitoring (capture every 2 seconds)
    capture.start_monitoring(interval=2.0, quality=60, verbose=False)
    logger.success("Monitoring started")

    # Simulate long-running process
    total_steps = 5
    for i in range(total_steps):
        logger.info(f"Processing step {i+1}/{total_steps}")
        time.sleep(3)  # Simulate work

        # Check monitoring status
        status = capture.get_status()
        logger.info(
            f"Screenshots captured so far: {status.get('screenshots_captured', 0)}"
        )

    # Stop monitoring
    capture.stop_monitoring()
    logger.success("Monitoring stopped")

    # Get final statistics
    status = capture.get_status()
    logger.info(f"Total screenshots: {status.get('screenshots_captured', 0)}")
    logger.info(f"Session ID: {status.get('session_id', 'N/A')}")


def create_debugging_timeline():
    """Create a GIF timeline for debugging review."""
    logger.info("Creating debugging timeline GIF")

    # List available sessions
    sessions = capture.list_sessions(limit=3)
    logger.info(f"Available sessions: {sessions}")

    if not sessions:
        logger.warning("No monitoring sessions available")
        logger.info("Run monitor_long_running_process() first")
        return

    # Create GIF from latest session
    try:
        gif_path = capture.create_gif(
            session_id="latest",
            duration=0.5,  # 0.5 seconds per frame
            max_frames=50,  # Limit to 50 frames
            optimize=True,
        )
        logger.success(f"Debugging timeline created: {gif_path}")
        logger.info("You can now review this GIF to see the process flow")
    except Exception as e:
        logger.error(f"Failed to create GIF: {e}")


def capture_error_state():
    """Example: Capture screenshots when errors occur."""
    logger.info("Demonstrating error state capture")

    try:
        # Simulate some work
        logger.info("Performing operation...")
        time.sleep(1)

        # Simulate an error condition
        raise ValueError("Simulated error for demonstration")

    except Exception as e:
        # Capture screenshot when error occurs
        error_screenshot = capture.screenshot(
            message=f"error_{type(e).__name__}",
            quality=95,  # High quality for debugging
        )
        logger.error(f"Error occurred: {e}")
        logger.info(f"Error state captured: {error_screenshot}")

        # You could also capture all windows for context
        info = capture.get_info()
        logger.info(f"System had {len(info.get('windows', []))} windows open")


def review_recent_captures():
    """Review and analyze recent screenshots."""
    logger.info("Reviewing recent captures")

    # List recent screenshots
    recent = capture.list_recent(limit=10, category="all")
    logger.info(f"Found {len(recent)} recent screenshots")

    # Analyze each screenshot (if available)
    for i, path in enumerate(recent[:3]):  # Analyze first 3
        logger.info(f"\nAnalyzing screenshot {i+1}: {path}")
        try:
            analysis = capture.analyze(path)
            logger.info(f"  Category: {analysis.get('category', 'unknown')}")
            logger.info(f"  Analysis: {analysis.get('message', 'N/A')}")
        except Exception as e:
            logger.warning(f"  Could not analyze: {e}")


def main():
    """Run debugging workflow examples."""
    logger.info("=" * 60)
    logger.info("Scitex Capture - Debugging Workflow Examples")
    logger.info("=" * 60)

    # Example 1: Simple automation with screenshots
    simulate_browser_automation()
    logger.info("-" * 60)

    # Example 2: Continuous monitoring (commented out - takes time)
    # monitor_long_running_process()
    # logger.info("-" * 60)
    # create_debugging_timeline()
    # logger.info("-" * 60)

    # Example 3: Error state capture
    capture_error_state()
    logger.info("-" * 60)

    # Example 4: Review captures
    review_recent_captures()

    logger.info("=" * 60)
    logger.success("Debugging workflow examples completed")


if __name__ == "__main__":
    main()

# EOF
