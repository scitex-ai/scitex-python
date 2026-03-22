#!/usr/bin/env python3
"""Save web pages as PDF using playwright's page.pdf() (print-style)."""

import asyncio
from pathlib import Path


async def _dismiss_overlays(page) -> None:
    """Dismiss cookie consent banners, popups, and sticky overlays."""
    # Common cookie consent button selectors
    _CONSENT_SELECTORS = [
        # Generic patterns
        "button:has-text('Accept all')",
        "button:has-text('Accept All')",
        "button:has-text('Accept all cookies')",
        "button:has-text('Accept All Cookies')",
        "button:has-text('Reject optional cookies')",
        "button:has-text('Reject all')",
        "button:has-text('I agree')",
        "button:has-text('Got it')",
        "button:has-text('OK')",
        "button:has-text('Close')",
        # ID/class patterns
        "[id*='cookie'] button",
        "[class*='cookie'] button",
        "[id*='consent'] button",
        "[class*='consent'] button",
        "[id*='gdpr'] button",
        "[class*='gdpr'] button",
    ]

    for selector in _CONSENT_SELECTORS:
        try:
            btn = page.locator(selector).first
            if await btn.is_visible(timeout=500):
                await btn.click(timeout=1000)
                await page.wait_for_timeout(500)
                break
        except Exception:
            continue

    # Remove any remaining fixed/sticky overlays via JS
    await page.evaluate("""
        () => {
            const remove = (el) => {
                const style = window.getComputedStyle(el);
                if (style.position === 'fixed' || style.position === 'sticky') {
                    const rect = el.getBoundingClientRect();
                    // Only remove large overlays (>30% of viewport width or height)
                    if (rect.width > window.innerWidth * 0.3
                        || rect.height > window.innerHeight * 0.3) {
                        el.remove();
                    }
                }
            };
            document.querySelectorAll('div, section, aside, footer, header')
                .forEach(remove);
        }
    """)
    await page.wait_for_timeout(300)


async def save_as_pdf_async(
    url: str,
    output_path: str,
    *,
    wait_seconds: float = 3,
    print_background: bool = True,
    format: str = "A4",
    margin_top: str = "10mm",
    margin_bottom: str = "10mm",
    margin_left: str = "10mm",
    margin_right: str = "10mm",
) -> str:
    """Navigate to URL and save page as PDF.

    Parameters
    ----------
    url : str
        URL to save as PDF.
    output_path : str
        Path to save the PDF file.
    wait_seconds : float
        Extra seconds to wait after page load for JS rendering.
    print_background : bool
        Whether to print background graphics.
    format : str
        Paper format (A4, Letter, etc.).
    margin_top, margin_bottom, margin_left, margin_right : str
        Page margins (e.g., "10mm", "1in").

    Returns
    -------
    str
        Absolute path of the saved PDF.
    """
    from playwright.async_api import async_playwright

    output = Path(output_path).expanduser().resolve()
    output.parent.mkdir(parents=True, exist_ok=True)

    # Ensure .pdf extension
    if output.suffix.lower() != ".pdf":
        output = output.with_suffix(".pdf")

    # Add scheme if missing
    if not url.startswith(("http://", "https://", "file://")):
        url = f"https://{url}"

    async with async_playwright() as pw:
        browser = await pw.chromium.launch(headless=True)
        page = await browser.new_page()

        await page.goto(url, wait_until="networkidle", timeout=60000)

        if wait_seconds > 0:
            await asyncio.sleep(wait_seconds)

        # Dismiss cookie consent banners and overlays before PDF capture
        await _dismiss_overlays(page)

        await page.pdf(
            path=str(output),
            format=format,
            print_background=print_background,
            margin={
                "top": margin_top,
                "bottom": margin_bottom,
                "left": margin_left,
                "right": margin_right,
            },
        )

        await browser.close()

    if not output.exists():
        raise RuntimeError(f"PDF was not created: {output}")

    size_kb = output.stat().st_size / 1024
    if size_kb < 1:
        raise RuntimeError(f"PDF too small ({size_kb:.1f} KB): {output}")

    return str(output)


def save_as_pdf(
    url: str,
    output_path: str,
    **kwargs,
) -> str:
    """Sync wrapper for save_as_pdf_async."""
    return asyncio.run(save_as_pdf_async(url, output_path, **kwargs))


# EOF
