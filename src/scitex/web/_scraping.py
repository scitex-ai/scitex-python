#!/usr/bin/env python3
# File: ./src/scitex/web/_scraping.py

"""Web scraping utilities for extracting URLs.

``bs4`` is an optional third-party dependency (only needed when actually
scraping). Do **not** import it at module load -- doing so leaks the
``ModuleNotFoundError`` through ``scitex.web.__init__`` and through
``scitex.cli.web``, which in turn breaks ``scitex --json`` and
``scitex --help-recursive`` on any install without ``beautifulsoup4``.
See ywatanabe1989/todo#279. The import now lives inside each scraping
function, so merely importing this module is side-effect-free.
"""

import re
import urllib.parse
from typing import List, Optional, Set

import requests

from scitex.logging import getLogger

logger = getLogger(__name__)

DEFAULT_TIMEOUT = 10
DEFAULT_USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"


def get_urls(
    url: str,
    pattern: Optional[str] = None,
    absolute: bool = True,
    same_domain: bool = False,
    include_external: bool = True,
) -> List[str]:
    """
    Extract all URLs from a webpage.

    Args:
        url: The URL of the webpage to scrape
        pattern: Optional regex pattern to filter URLs (e.g., r'\\.pdf$' for PDF files)
        absolute: If True, convert relative URLs to absolute URLs
        same_domain: If True, only return URLs from the same domain
        include_external: If True, include external links (only applies if same_domain=False)

    Returns:
        List of URLs found on the page

    Example:
        >>> urls = get_urls('https://example.com', pattern=r'\\.pdf$')
        >>> urls = get_urls('https://example.com', same_domain=True)
    """
    from bs4 import BeautifulSoup  # lazy: see module docstring, todo#279

    try:
        logger.info(f"Fetching URLs from: {url}")
        response = requests.get(
            url,
            timeout=DEFAULT_TIMEOUT,
            headers={"User-Agent": DEFAULT_USER_AGENT},
        )
        response.raise_for_status()
    except requests.RequestException as e:
        logger.error(f"Failed to fetch URL {url}: {e}")
        return []

    soup = BeautifulSoup(response.text, "html.parser")
    urls_found: Set[str] = set()

    parsed_base = urllib.parse.urlparse(url)

    for link in soup.find_all("a", href=True):
        href = link["href"]

        if absolute:
            href = urllib.parse.urljoin(url, href)

        if same_domain:
            parsed_href = urllib.parse.urlparse(href)
            if parsed_href.netloc != parsed_base.netloc:
                continue
        elif not include_external:
            parsed_href = urllib.parse.urlparse(href)
            if parsed_href.netloc and parsed_href.netloc != parsed_base.netloc:
                continue

        if pattern and not re.search(pattern, href):
            continue

        urls_found.add(href)

    result = sorted(list(urls_found))
    logger.info(f"Found {len(result)} URLs")
    return result


def get_image_urls(
    url: str,
    pattern: Optional[str] = None,
    same_domain: bool = False,
) -> List[str]:
    """
    Extract all image URLs from a webpage without downloading them.

    Args:
        url: The URL of the webpage to scrape
        pattern: Optional regex pattern to filter image URLs
        same_domain: If True, only return images from the same domain

    Returns:
        List of image URLs found on the page

    Note:
        - SVG files are automatically skipped (vector graphics)
        - Checks both 'src' and 'data-src' attributes for lazy-loaded images

    Example:
        >>> img_urls = get_image_urls('https://example.com')
        >>> img_urls = get_image_urls('https://example.com', pattern=r'\\.png$')
    """
    from bs4 import BeautifulSoup  # lazy: see module docstring, todo#279

    try:
        logger.info(f"Fetching image URLs from: {url}")
        response = requests.get(
            url,
            timeout=DEFAULT_TIMEOUT,
            headers={"User-Agent": DEFAULT_USER_AGENT},
        )
        response.raise_for_status()
    except requests.RequestException as e:
        logger.error(f"Failed to fetch URL {url}: {e}")
        return []

    soup = BeautifulSoup(response.text, "html.parser")
    image_urls: Set[str] = set()

    parsed_base = urllib.parse.urlparse(url)

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

        if pattern and not re.search(pattern, img_url):
            continue

        image_urls.add(img_url)

    result = sorted(list(image_urls))
    logger.info(f"Found {len(result)} image URLs")
    return result
