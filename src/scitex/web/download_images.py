#!/usr/bin/env python3
# File: ./src/scitex/web/download_images.py

"""
Image Downloader for SciTeX.

Downloads images from URLs with minimum size filtering.

Usage:
    python -m scitex.web.download_images https://example.com
    python -m scitex.web.download_images https://example.com -o ./downloads
    python -m scitex.web.download_images https://example.com --min-size 800x600
"""

import os
import re
import urllib.parse
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Tuple

import requests
from tqdm import tqdm

# NOTE: ``bs4`` is imported lazily inside functions that actually use it.
# Importing at module load leaks ``ModuleNotFoundError`` through
# ``scitex.web.__init__`` and breaks ``scitex --json`` /
# ``scitex --help-recursive`` on installs without beautifulsoup4.
# See ywatanabe1989/todo#279.

try:
    from io import BytesIO

    from PIL import Image

    PILLOW_AVAILABLE = True
except ImportError:
    PILLOW_AVAILABLE = False

from scitex.logging import getLogger

logger = getLogger(__name__)

# Configuration
DEFAULT_MIN_WIDTH = 400
DEFAULT_MIN_HEIGHT = 300
DEFAULT_TIMEOUT = 10
DEFAULT_USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"


def _get_default_download_dir() -> str:
    """Get default download directory using SCITEX_DIR if available."""
    scitex_root = os.environ.get("SCITEX_DIR", os.path.expanduser("~/.scitex"))
    return os.path.join(scitex_root, "web", "downloads")


def _normalize_url_for_directory(url: str) -> str:
    """Convert URL to a safe directory name."""
    parsed = urllib.parse.urlparse(url)
    domain = parsed.netloc.replace("www.", "")
    path = parsed.path.strip("/").replace("/", "-")

    normalized = f"{domain}-{path}" if path else domain
    normalized = re.sub(r"[^\w\-.]", "-", normalized)
    normalized = re.sub(r"-+", "-", normalized)
    normalized = normalized[:100].strip("-")

    return normalized


def _is_direct_image_url(url: str) -> bool:
    """Check if URL appears to be a direct image link."""
    extensions = [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp"]
    path = urllib.parse.urlparse(url.lower()).path
    return any(path.endswith(ext) for ext in extensions)


def _extract_image_urls(url: str, same_domain: bool = False) -> List[str]:
    """Extract image URLs from a webpage."""
    from bs4 import BeautifulSoup  # lazy: see module note, todo#279

    try:
        logger.info(f"Fetching page: {url}")
        response = requests.get(
            url,
            timeout=DEFAULT_TIMEOUT,
            headers={"User-Agent": DEFAULT_USER_AGENT},
        )
        response.raise_for_status()
    except requests.RequestException as e:
        logger.error(f"Failed to fetch page: {e}")
        return []

    soup = BeautifulSoup(response.content, "html.parser")
    parsed_base = urllib.parse.urlparse(url)
    image_urls = set()

    for img in soup.find_all("img"):
        img_url = img.get("src") or img.get("data-src")
        if not img_url:
            continue

        img_url = urllib.parse.urljoin(url, img_url)

        if img_url.lower().endswith((".svg", ".svgz")):
            continue

        if same_domain:
            parsed_img = urllib.parse.urlparse(img_url)
            if parsed_img.netloc != parsed_base.netloc:
                continue

        image_urls.add(img_url)

    logger.info(f"Found {len(image_urls)} images on page")
    return list(image_urls)


def _download_single_image(
    img_url: str,
    output_dir: Path,
    counter: int,
    min_size: Optional[Tuple[int, int]],
) -> Optional[str]:
    """Download a single image."""
    try:
        response = requests.get(
            img_url,
            timeout=DEFAULT_TIMEOUT,
            headers={"User-Agent": DEFAULT_USER_AGENT},
        )
        response.raise_for_status()

        # Validate content-type
        content_type = response.headers.get("content-type", "")
        if not content_type.startswith("image/"):
            logger.debug(f"Skipping non-image: {content_type}")
            return None

        # Check dimensions
        if min_size and PILLOW_AVAILABLE:
            try:
                img = Image.open(BytesIO(response.content))
                width, height = img.size
                if width < min_size[0] or height < min_size[1]:
                    logger.debug(
                        f"Skipping small image: {width}x{height} "
                        f"(min: {min_size[0]}x{min_size[1]})"
                    )
                    return None
            except Exception:
                pass

        # Determine extension
        ext = "jpg"
        if PILLOW_AVAILABLE:
            try:
                img = Image.open(BytesIO(response.content))
                fmt = img.format.lower() if img.format else "jpeg"
                ext = "jpg" if fmt == "jpeg" else fmt
            except Exception:
                pass
        elif "png" in content_type:
            ext = "png"
        elif "gif" in content_type:
            ext = "gif"
        elif "webp" in content_type:
            ext = "webp"

        filename = f"{counter:04d}.{ext}"
        filepath = output_dir / filename

        with open(filepath, "wb") as f:
            f.write(response.content)

        logger.info(f"Downloaded: {filename}")
        return str(filepath)

    except Exception as e:
        logger.warning(f"Error downloading {img_url}: {e}")
        return None


def download_images(
    url: str,
    output_dir: Optional[str] = None,
    min_size: Optional[Tuple[int, int]] = None,
    max_workers: int = 5,
    same_domain: bool = False,
) -> List[str]:
    """
    Download images from a URL.

    Args:
        url: Webpage URL or direct image URL
        output_dir: Output directory (default: $SCITEX_DIR/web/downloads)
        min_size: Minimum (width, height) to filter small images (default: 400x300)
        max_workers: Concurrent download threads
        same_domain: Only download images from the same domain

    Returns:
        List of downloaded file paths

    Example:
        >>> paths = download_images("https://example.com")
        >>> paths = download_images("https://example.com/photo.jpg")
        >>> paths = download_images("https://example.com", min_size=(800, 600))
    """
    if not PILLOW_AVAILABLE:
        logger.warning("Pillow not available. Size filtering disabled.")
        min_size = None
    elif min_size is None:
        min_size = (DEFAULT_MIN_WIDTH, DEFAULT_MIN_HEIGHT)

    # Setup output directory
    if output_dir is None:
        output_dir = os.environ.get("SCITEX_WEB_DOWNLOADS_DIR")
        if output_dir is None:
            output_dir = _get_default_download_dir()

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    normalized = _normalize_url_for_directory(url)
    output_path = Path(output_dir).expanduser() / f"{timestamp}-{normalized}-images"
    output_path.mkdir(parents=True, exist_ok=True)

    logger.info(f"Output directory: {output_path}")

    # Get image URLs
    if _is_direct_image_url(url):
        image_urls = [url]
        logger.info("Direct image URL detected")
    else:
        image_urls = _extract_image_urls(url, same_domain=same_domain)

    if not image_urls:
        logger.warning("No images found")
        return []

    # Download concurrently
    downloaded = []
    counter = [1]

    def download_with_counter(img_url: str) -> Optional[str]:
        idx = counter[0]
        counter[0] += 1
        return _download_single_image(img_url, output_path, idx, min_size)

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(download_with_counter, u): u for u in image_urls}

        for future in tqdm(
            as_completed(futures), total=len(image_urls), desc="Downloading"
        ):
            result = future.result()
            if result:
                downloaded.append(result)

    logger.info(f"Downloaded {len(downloaded)} images to {output_path}")
    return downloaded


def main():
    """CLI entry point."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Download images from URL",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python -m scitex.web.download_images https://example.com
  python -m scitex.web.download_images https://example.com -o ./downloads
  python -m scitex.web.download_images https://example.com --min-size 800x600
  python -m scitex.web.download_images https://example.com --no-min-size
        """,
    )
    parser.add_argument("url", help="URL to download images from")
    parser.add_argument("-o", "--output", help="Output directory")
    parser.add_argument(
        "--min-size",
        default="400x300",
        help="Minimum size WIDTHxHEIGHT (default: 400x300)",
    )
    parser.add_argument(
        "--no-min-size",
        action="store_true",
        help="Disable size filtering",
    )
    parser.add_argument(
        "--same-domain",
        action="store_true",
        help="Only download from same domain",
    )
    parser.add_argument(
        "--workers",
        type=int,
        default=5,
        help="Concurrent downloads (default: 5)",
    )

    args = parser.parse_args()

    min_size = None
    if not args.no_min_size and args.min_size:
        w, h = map(int, args.min_size.split("x"))
        min_size = (w, h)

    paths = download_images(
        args.url,
        output_dir=args.output,
        min_size=min_size,
        max_workers=args.workers,
        same_domain=args.same_domain,
    )

    print(f"\nDownloaded {len(paths)} images:")
    for p in paths:
        print(f"  {p}")


if __name__ == "__main__":
    main()
