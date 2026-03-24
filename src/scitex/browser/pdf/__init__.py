#!/usr/bin/env python3
# SciTeX Browser PDF Utilities
# ----------------------------------------

from ._save_as_pdf import save_as_pdf, save_as_pdf_async
from .click_download_for_chrome_pdf_viewer import (
    click_download_for_chrome_pdf_viewer_async,
)
from .detect_chrome_pdf_viewer import detect_chrome_pdf_viewer_async

__all__ = [
    "save_as_pdf",
    "save_as_pdf_async",
    "detect_chrome_pdf_viewer_async",
    "click_download_for_chrome_pdf_viewer_async",
]

# EOF
