#!/usr/bin/env python3
"""
SciTeX CLI - Web Scraping Commands
"""

import subprocess
import sys
from datetime import datetime
from pathlib import Path

import click

from scitex.logging import getLogger
from scitex.web import download_images, get_image_urls, get_urls
from scitex.web.download_images import _get_default_download_dir

logger = getLogger(__name__)


@click.group(invoke_without_command=True)
@click.option(
    "--json",
    "as_json",
    is_flag=True,
    help="Output as structured JSON (Result envelope).",
)
@click.pass_context
def web(ctx, as_json):
    """
    Web scraping utilities

    \b
    Commands:
      get-urls        Extract URLs from a webpage
      get-image-urls  Extract image URLs from a webpage
      download-images Download images from a webpage
      take-screenshot Capture a screenshot of a webpage

    \b
    Examples:
      scitex web get-urls https://example.com
      scitex web get-urls https://example.com --pattern "\\.pdf$"
      scitex web get-image-urls https://example.com
      scitex web download-images https://example.com --output ./downloads
      scitex web download-images https://example.com --min-size 100x100
      scitex web take-screenshot https://example.com
      scitex web take-screenshot https://example.com --output ./screenshots
    """
    if ctx.invoked_subcommand is None:
        if as_json:
            from . import group_to_json

            group_to_json(ctx, web)
        else:
            click.echo(ctx.get_help())


@web.command()
@click.argument("url")
@click.option(
    "--pattern",
    "-p",
    help='Regex pattern to filter URLs (e.g., "\\.pdf$" for PDF files)',
)
@click.option(
    "--same-domain", is_flag=True, help="Only include URLs from the same domain"
)
@click.option(
    "--relative",
    is_flag=True,
    help="Keep URLs as relative instead of converting to absolute",
)
@click.option(
    "--output",
    "-o",
    type=click.Path(),
    help="Save URLs to file instead of printing to stdout",
)
def get_urls_cmd(url, pattern, same_domain, relative, output):
    """Extract all URLs from a webpage."""
    try:
        click.echo(f"Extracting URLs from: {url}")

        urls = get_urls(
            url, pattern=pattern, absolute=not relative, same_domain=same_domain
        )

        if not urls:
            click.secho("No URLs found", fg="yellow")
            sys.exit(0)

        click.secho(f"Found {len(urls)} URLs", fg="green")

        if output:
            output_path = Path(output)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, "w") as f:
                f.write("\n".join(urls))
            click.echo(f"URLs saved to: {output_path}")
        else:
            click.echo()
            for url_item in urls:
                click.echo(url_item)

        sys.exit(0)

    except Exception as e:
        click.secho(f"ERROR: {e}", fg="red", err=True)
        sys.exit(1)


@web.command()
@click.argument("url")
@click.option(
    "--pattern", "-p", help='Regex pattern to filter image URLs (e.g., "\\.jpg$")'
)
@click.option(
    "--same-domain", is_flag=True, help="Only include images from the same domain"
)
@click.option(
    "--output",
    "-o",
    type=click.Path(),
    help="Save image URLs to file instead of printing to stdout",
)
def get_image_urls_cmd(url, pattern, same_domain, output):
    """Extract image URLs from a webpage without downloading them."""
    try:
        click.echo(f"Extracting image URLs from: {url}")

        img_urls = get_image_urls(url, pattern=pattern, same_domain=same_domain)

        if not img_urls:
            click.secho("No image URLs found", fg="yellow")
            sys.exit(0)

        click.secho(f"Found {len(img_urls)} image URLs", fg="green")

        if output:
            output_path = Path(output)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, "w") as f:
                f.write("\n".join(img_urls))
            click.echo(f"Image URLs saved to: {output_path}")
        else:
            click.echo()
            for img_url in img_urls:
                click.echo(img_url)

        sys.exit(0)

    except Exception as e:
        click.secho(f"ERROR: {e}", fg="red", err=True)
        sys.exit(1)


@web.command()
@click.argument("url")
@click.option(
    "--output",
    "-o",
    type=click.Path(),
    help="Output directory (default: $SCITEX_WEB_DOWNLOADS_DIR or $SCITEX_DIR/web/downloads)",
)
@click.option(
    "--pattern", "-p", help='Regex pattern to filter image URLs (e.g., "\\.jpg$")'
)
@click.option(
    "--min-size",
    default="100x100",
    help="Minimum image size as WIDTHxHEIGHT (default: 100x100)",
)
@click.option(
    "--same-domain", is_flag=True, help="Only download images from the same domain"
)
@click.option(
    "--max-workers",
    type=int,
    default=5,
    help="Number of concurrent download threads (default: 5)",
)
def download_images_cmd(url, output, pattern, min_size, same_domain, max_workers):
    """
    Download all images from a webpage.

    \b
    Output directory priority:
      1. --output option if specified
      2. SCITEX_WEB_DOWNLOADS_DIR environment variable
      3. $SCITEX_DIR/web/downloads (default)

    \b
    Note:
      - Images are saved in a timestamped subdirectory: images-YYYYMMDD_HHMMSS/
      - Only images >= 100x100 pixels are downloaded by default
      - SVG files are automatically skipped (vector graphics)
    """
    try:
        click.echo(f"Downloading images from: {url}")

        # Parse min_size if provided
        min_size_tuple = None
        if min_size:
            try:
                width, height = map(int, min_size.split("x"))
                min_size_tuple = (width, height)
            except ValueError:
                click.secho(
                    "ERROR: Invalid min-size format. Use WIDTHxHEIGHT (e.g., '100x100')",
                    fg="red",
                    err=True,
                )
                sys.exit(1)

        paths = download_images(
            url,
            output_dir=output,
            pattern=pattern,
            min_size=min_size_tuple,
            max_workers=max_workers,
            same_domain=same_domain,
        )

        if not paths:
            click.secho("No images downloaded", fg="yellow")
            sys.exit(0)

        # Show where images were saved (get actual directory from first path)
        if paths:
            actual_output = str(Path(paths[0]).parent)
        else:
            actual_output = output or _get_default_download_dir()

        click.secho(f"Successfully downloaded {len(paths)} images", fg="green")
        click.echo(f"Images saved to: {actual_output}")

        sys.exit(0)

    except Exception as e:
        click.secho(f"ERROR: {e}", fg="red", err=True)
        sys.exit(1)


@web.command()
@click.argument("url")
@click.option(
    "--output",
    "-o",
    type=click.Path(),
    help="Output directory for the screenshot (default: ~/.scitex/capture)",
)
@click.option(
    "--message", "-m", help="Optional message to include in the screenshot filename"
)
@click.option(
    "--quality", "-q", type=int, default=85, help="JPEG quality 1-100 (default: 85)"
)
@click.option(
    "--full-page",
    is_flag=True,
    help="Capture the full page (scrolling) instead of just viewport",
)
def take_screenshot_cmd(url, output, message, quality, full_page):
    """
    Capture a screenshot of a webpage.

    \b
    Output directory priority:
      1. --output option if specified
      2. ~/.scitex/capture (default)

    \b
    Features:
      - Captures webpage screenshots with timestamps
      - Supports custom messages in filenames for organization
      - Adjustable quality settings
      - Full page or viewport-only capture

    \b
    Examples:
      scitex web take-screenshot https://example.com
      scitex web take-screenshot https://example.com --output ./screenshots
      scitex web take-screenshot https://example.com --message "homepage-test"
      scitex web take-screenshot https://example.com --quality 95 --full-page
    """
    try:
        click.echo(f"Capturing screenshot of: {url}")

        # Prepare output directory
        if output:
            output_path = Path(output).resolve()
            output_path.mkdir(parents=True, exist_ok=True)
            output_dir = str(output_path)
        else:
            output_dir = str(Path.home() / ".scitex" / "capture")
            Path(output_dir).mkdir(parents=True, exist_ok=True)

        # Generate timestamped filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        if message:
            filename = f"screenshot_{timestamp}_{message}.png"
        else:
            filename = f"screenshot_{timestamp}.png"

        output_file = Path(output_dir) / filename

        # Use playwright MCP server to take screenshot
        # We'll use a simple approach: navigate to URL and take screenshot
        cmd = ["playwright", "screenshot", url, str(output_file)]

        # Try using the MCP approach first, fall back to direct playwright if available
        try:
            # For now, we'll use a simpler approach with playwright directly
            import asyncio

            from playwright.async_api import async_playwright

            async def capture():
                async with async_playwright() as p:
                    browser = await p.chromium.launch()
                    page = await browser.new_page()
                    await page.goto(url)
                    await page.screenshot(
                        path=str(output_file),
                        full_page=full_page,
                        type="png" if str(output_file).endswith(".png") else "jpeg",
                        quality=(
                            quality
                            if str(output_file).endswith(".jpg")
                            or str(output_file).endswith(".jpeg")
                            else None
                        ),
                    )
                    await browser.close()

            asyncio.run(capture())

            if output_file.exists():
                click.secho("Screenshot saved successfully", fg="green")
                click.echo(f"Location: {output_file}")
                sys.exit(0)
            else:
                raise Exception("Screenshot file was not created")

        except ImportError:
            # Fall back to using playwright CLI if the Python package is not available
            click.secho(
                "Playwright Python package not found, trying CLI...", fg="yellow"
            )
            result = subprocess.run(
                ["playwright", "screenshot", url, str(output_file)],
                capture_output=True,
                text=True,
            )

            if result.returncode == 0 and output_file.exists():
                click.secho("Screenshot saved successfully", fg="green")
                click.echo(f"Location: {output_file}")
                sys.exit(0)
            else:
                raise Exception(f"Playwright CLI failed: {result.stderr}")

    except Exception as e:
        error_msg = str(e)
        click.secho(f"ERROR: {error_msg}", fg="red", err=True)
        click.echo()

        # Provide context-specific troubleshooting
        if "ERR_CONNECTION_REFUSED" in error_msg or "Connection refused" in error_msg:
            click.echo("Troubleshooting - Connection Refused:")
            click.echo("  1. Make sure a web server is running at the specified URL")
            click.echo(
                "  2. Check if the port is correct (e.g., http://127.0.0.1:8000/)"
            )
            click.echo("  3. Verify the server is accessible: curl <url>")
            click.echo(
                "  4. If using WSL, you may need to use the WSL IP instead of 127.0.0.1"
            )
        elif (
            "ERR_NAME_NOT_RESOLVED" in error_msg
            or "Name or service not known" in error_msg
        ):
            click.echo("Troubleshooting - DNS Resolution Failed:")
            click.echo("  1. Check if the domain name is correct")
            click.echo("  2. Verify internet connection")
            click.echo("  3. Try pinging the domain: ping <domain>")
        elif "Timeout" in error_msg or "timeout" in error_msg:
            click.echo("Troubleshooting - Connection Timeout:")
            click.echo("  1. The server may be slow to respond")
            click.echo("  2. Check network connectivity")
            click.echo("  3. Try accessing the URL in a regular browser")
        elif "No module named 'playwright'" in error_msg or "ImportError" in error_msg:
            click.echo("Troubleshooting - Playwright Not Installed:")
            click.echo("  1. Install Playwright: pip install playwright")
            click.echo("  2. Install browsers: playwright install chromium")
        elif (
            "Executable doesn't exist" in error_msg
            or "browser executable" in error_msg.lower()
        ):
            click.echo("Troubleshooting - Browser Not Installed:")
            click.echo("  1. Install Chromium browser: playwright install chromium")
            click.echo("  2. Or install all browsers: playwright install")
        else:
            click.echo("Troubleshooting:")
            click.echo("  1. Verify the URL is accessible in a regular browser")
            click.echo("  2. Check Playwright installation: pip install playwright")
            click.echo("  3. Check browser installation: playwright install chromium")

        sys.exit(1)


# Register command aliases
web.add_command(get_urls_cmd, name="get-urls")
web.add_command(get_image_urls_cmd, name="get-image-urls")
web.add_command(download_images_cmd, name="download-images")
web.add_command(take_screenshot_cmd, name="take-screenshot")


if __name__ == "__main__":
    web()
