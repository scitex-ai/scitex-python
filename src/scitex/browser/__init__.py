#!/usr/bin/env python3
# SciTeX Browser Utilities - Universal Playwright helpers organized by category
# ----------------------------------------

# All browser utilities require playwright - make them optional

# Debugging utilities
try:
    from .debugging import (  # Sync browser session for zombie prevention; Test monitoring (periodic screenshots via scitex.capture); Visual cursor/feedback utilities (sync and async); Failure capture utilities (mirrors console-interceptor.ts)
        SyncBrowserSession,
        TestMonitor,
        browser_logger,
        collect_console_logs,
        collect_console_logs_detailed,
        create_browser_session_fixture,
        create_failure_capture_fixture,
        create_test_monitor_fixture,
        format_logs_devtools_style,
        highlight_element_async,
        inject_visual_effects,
        inject_visual_effects_async,
        monitor_test,
        save_failure_artifacts,
        setup_console_interceptor,
        show_click_effect,
        show_click_effect_async,
        show_cursor_at,
        show_cursor_at_async,
        show_grid_async,
        show_step,
        show_step_async,
        show_test_result,
        show_test_result_async,
        sync_browser_session,
    )
except ImportError:
    browser_logger = None
    show_grid_async = None
    highlight_element_async = None
    inject_visual_effects = None
    inject_visual_effects_async = None
    show_cursor_at = None
    show_cursor_at_async = None
    show_click_effect = None
    show_click_effect_async = None
    show_step = None
    show_step_async = None
    show_test_result = None
    show_test_result_async = None
    setup_console_interceptor = None
    collect_console_logs = None
    collect_console_logs_detailed = None
    format_logs_devtools_style = None
    save_failure_artifacts = None
    create_failure_capture_fixture = None
    TestMonitor = None
    create_test_monitor_fixture = None
    monitor_test = None
    SyncBrowserSession = None
    sync_browser_session = None
    create_browser_session_fixture = None

# PDF utilities
try:
    from .pdf import (
        click_download_for_chrome_pdf_viewer_async,
        detect_chrome_pdf_viewer_async,
        save_as_pdf,
        save_as_pdf_async,
    )
except ImportError:
    detect_chrome_pdf_viewer_async = None
    click_download_for_chrome_pdf_viewer_async = None
    save_as_pdf = None
    save_as_pdf_async = None

# Interaction utilities
try:
    from .interaction import (
        PopupHandler,
        click_center_async,
        click_with_fallbacks_async,
        close_popups_async,
        ensure_no_popups_async,
        fill_with_fallbacks_async,
    )
except ImportError:
    click_center_async = None
    click_with_fallbacks_async = None
    fill_with_fallbacks_async = None
    PopupHandler = None
    close_popups_async = None
    ensure_no_popups_async = None


def is_playwright_cli_available() -> bool:
    """Check if playwright-cli (npm) is installed."""
    import shutil

    return shutil.which("playwright-cli") is not None


__all__ = [
    # Utilities
    "is_playwright_cli_available",
    # Debugging
    "browser_logger",
    "show_grid_async",
    "highlight_element_async",
    # Visual cursor/feedback (sync)
    "inject_visual_effects",
    "show_cursor_at",
    "show_click_effect",
    "show_step",
    "show_test_result",
    # Visual cursor/feedback (async)
    "inject_visual_effects_async",
    "show_cursor_at_async",
    "show_click_effect_async",
    "show_step_async",
    "show_test_result_async",
    # Failure capture utilities (mirrors console-interceptor.ts)
    "setup_console_interceptor",
    "collect_console_logs",
    "collect_console_logs_detailed",
    "format_logs_devtools_style",
    "save_failure_artifacts",
    "create_failure_capture_fixture",
    # Test monitoring (periodic screenshots via scitex.capture)
    "TestMonitor",
    "create_test_monitor_fixture",
    "monitor_test",
    # Sync browser session for zombie prevention
    "SyncBrowserSession",
    "sync_browser_session",
    "create_browser_session_fixture",
    # PDF
    "save_as_pdf",
    "save_as_pdf_async",
    "detect_chrome_pdf_viewer_async",
    "click_download_for_chrome_pdf_viewer_async",
    # Interaction
    "click_center_async",
    "click_with_fallbacks_async",
    "fill_with_fallbacks_async",
    "PopupHandler",
    "close_popups_async",
    "ensure_no_popups_async",
]

# EOF
