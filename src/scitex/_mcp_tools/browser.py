#!/usr/bin/env python3
"""Browser module tools for FastMCP unified server."""


def register_browser_tools(mcp) -> None:
    """Register browser tools with FastMCP server."""

    @mcp.tool()
    async def browser_save_as_pdf(
        url: str,
        output_path: str,
        wait_seconds: float = 3,
        print_background: bool = True,
        format: str = "A4",
        margin: str = "10mm",
    ) -> str:
        """Save a web page as PDF (print-style, like browser print-to-PDF).

        Args:
            url: URL to save as PDF.
            output_path: Path to save the PDF file.
            wait_seconds: Extra seconds to wait after page load for JS rendering.
            print_background: Whether to print background graphics.
            format: Paper format (A4, Letter, etc.).
            margin: Page margins (e.g., 10mm, 1in).
        """
        from scitex_dev.mcp_utils import async_wrap_as_mcp

        from scitex.browser.pdf._save_as_pdf import save_as_pdf_async

        return await async_wrap_as_mcp(
            save_as_pdf_async,
            side_effects=["file_create: PDF file"],
            url=url,
            output_path=output_path,
            wait_seconds=wait_seconds,
            print_background=print_background,
            format=format,
            margin_top=margin,
            margin_bottom=margin,
            margin_left=margin,
            margin_right=margin,
        )


# EOF
