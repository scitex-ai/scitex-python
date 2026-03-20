#!/usr/bin/env python3
"""Open browser with download monitoring and auto-linking.

This CLI tool opens a visible browser and monitors downloads, automatically
moving downloaded PDFs to the correct library location.

Usage:
    # Monitor downloads and auto-link
    python -m scitex.scholar.cli.open_browser_monitored --project neurovista

    # Monitor pending papers only
    python -m scitex.scholar.cli.open_browser_monitored --project neurovista --pending
"""

import argparse
import json
import shutil
import sys
import time
from pathlib import Path
from typing import Dict, List, Optional

from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from scitex.logging import getLogger
from scitex.scholar.config import ScholarConfig

logger = getLogger(__name__)


class DownloadMonitor(FileSystemEventHandler):
    """Monitor downloads folder and link PDFs to library."""

    def __init__(
        self, paper_id_map: Dict[str, str], library_manager, config: ScholarConfig
    ):
        """
        Args:
            paper_id_map: Maps download filenames to paper_ids
            library_manager: LibraryManager instance for organizing files
            config: Scholar configuration
        """
        self.name = self.__class__.__name__
        self.paper_id_map = paper_id_map
        self.library_manager = library_manager
        self.config = config
        self.processed_files = set()

    def on_created(self, event):
        """Handle new file creation in downloads folder."""
        if event.is_directory:
            return

        file_path = Path(event.src_path)

        # Only process PDF files
        if file_path.suffix.lower() != ".pdf":
            return

        # Avoid processing the same file twice
        if str(file_path) in self.processed_files:
            return

        # Wait for file to finish downloading
        time.sleep(2)
        if not file_path.exists():
            return

        logger.info(f"New PDF detected: {file_path.name}")

        # Try to match to a paper
        paper_id = self._match_pdf_to_paper(file_path)

        if paper_id:
            self._link_pdf_to_library(file_path, paper_id)
            self.processed_files.add(str(file_path))
        else:
            logger.warning(f"Could not match PDF to any paper: {file_path.name}")

    def _match_pdf_to_paper(self, pdf_path: Path) -> Optional[str]:
        """Match downloaded PDF to paper_id.

        Tries multiple matching strategies:
        1. Exact filename match in map
        2. Partial filename match
        3. PDF content matching (DOI, title)
        """
        filename = pdf_path.name

        # Strategy 1: Exact match
        if filename in self.paper_id_map:
            return self.paper_id_map[filename]

        # Strategy 2: Partial match (common with browser renames)
        for map_name, paper_id in self.paper_id_map.items():
            if map_name in filename or filename in map_name:
                logger.info(f"Partial match: {filename} -> {paper_id}")
                return paper_id

        # Strategy 3: Extract and match metadata from PDF
        try:
            from pypdf import PdfReader

            reader = PdfReader(pdf_path)

            # Check PDF metadata
            if reader.metadata:
                pdf_title = reader.metadata.get("/Title", "").lower()

                # Match against paper titles
                for paper_id, title in self.paper_id_map.items():
                    if isinstance(title, str) and title.lower() in pdf_title:
                        logger.info(f"Title match from PDF metadata: {paper_id}")
                        return paper_id

            # Check first page for DOI
            if len(reader.pages) > 0:
                first_page = reader.pages[0].extract_text()

                # Look for DOI pattern
                import re

                doi_match = re.search(r"10\.\d{4,}/[^\s]+", first_page)
                if doi_match:
                    doi = doi_match.group()
                    for paper_id, paper_doi in self.paper_id_map.items():
                        if isinstance(paper_doi, str) and doi in paper_doi:
                            logger.info(f"DOI match from PDF content: {paper_id}")
                            return paper_id
        except Exception as e:
            logger.warning(f"Could not extract PDF metadata: {e}")

        return None

    def _link_pdf_to_library(self, pdf_path: Path, paper_id: str):
        """Move PDF to correct library location and update metadata."""
        try:
            # Get paper directory
            master_dir = self.config.path_manager.get_library_master_dir()
            paper_dir = master_dir / paper_id

            if not paper_dir.exists():
                logger.error(f"Paper directory not found: {paper_dir}")
                return

            # Read metadata to get proper filename
            metadata_file = paper_dir / "metadata.json"
            if metadata_file.exists():
                with open(metadata_file) as f:
                    metadata = json.load(f)

                # Generate proper filename
                meta = metadata.get("metadata", {})
                basic = meta.get("basic", {})

                year = basic.get("year", "XXXX")
                first_author = basic.get("first_author_lastname", "Unknown")
                journal = basic.get("journal", "Unknown")

                # Clean filename
                journal_clean = "".join(
                    c for c in journal if c.isalnum() or c in (" ", "-", "_")
                )[:50]
                proper_name = f"{first_author}-{year}-{journal_clean}.pdf"
            else:
                # Fallback to original name
                proper_name = pdf_path.name

            # Move PDF to paper directory
            dest_path = paper_dir / proper_name
            shutil.move(str(pdf_path), str(dest_path))

            logger.success(f"Linked PDF: {proper_name} -> {paper_id}")
            logger.info(f"Location: {dest_path}")

            # Update symlinks to reflect PDF_s status

            # Trigger symlink update by touching metadata
            if metadata_file.exists():
                metadata_file.touch()

        except Exception as e:
            logger.error(f"Failed to link PDF: {e}")


def get_failed_papers(project: str, config: ScholarConfig) -> List[Dict]:
    """Get papers with failed downloads - reuse from open_browser.py"""
    from scitex.scholar.cli.open_browser import get_failed_papers as _get_failed

    return _get_failed(project, config)


def get_pending_papers(project: str, config: ScholarConfig) -> List[Dict]:
    """Get papers with pending downloads - reuse from open_browser.py"""
    from scitex.scholar.cli.open_browser import get_pending_papers as _get_pending

    return _get_pending(project, config)


def open_browser_with_monitoring(
    papers: List[Dict],
    project: str,
    config: ScholarConfig,
    profile: str = None,
    downloads_dir: Path = None,
) -> None:
    """Open browser and monitor downloads for auto-linking.

    Args:
        papers: List of paper metadata dicts
        project: Project name
        config: Scholar configuration
        profile: Browser profile name
        downloads_dir: Downloads directory to monitor
    """
    from playwright.sync_api import sync_playwright

    if not papers:
        logger.info("No papers to open")
        return

    # Build paper_id map for download matching
    paper_id_map = {}
    urls_to_open = []

    for paper in papers:
        paper_id = paper.get("paper_id")
        if not paper_id:
            continue

        # Store multiple identifiers for matching
        paper_id_map[paper_id] = paper_id

        # Store title for matching
        title = paper.get("title", "")
        if title:
            paper_id_map[title] = paper_id

        # Store DOI for matching
        doi = paper.get("doi", "")
        if doi:
            paper_id_map[doi] = paper_id

        # Get URL to open
        if paper.get("openurl_resolved") and len(paper["openurl_resolved"]) > 0:
            urls_to_open.append((paper_id, paper["openurl_resolved"][0]))
        elif paper.get("url_publisher"):
            urls_to_open.append((paper_id, paper["url_publisher"]))
        elif paper.get("url_doi"):
            urls_to_open.append((paper_id, paper["url_doi"]))

    if not urls_to_open:
        logger.warning("No URLs to open")
        return

    # Get downloads directory
    if downloads_dir is None:
        downloads_dir = Path.home() / "Downloads"
    downloads_dir = Path(downloads_dir)

    if not downloads_dir.exists():
        logger.error(f"Downloads directory not found: {downloads_dir}")
        return

    logger.info(f"Monitoring downloads in: {downloads_dir}")
    logger.info(f"Opening {len(urls_to_open)} URLs in browser...")

    # Setup download monitor
    from scitex.scholar.storage._LibraryManager import LibraryManager

    library_manager = LibraryManager(config)

    event_handler = DownloadMonitor(paper_id_map, library_manager, config)
    observer = Observer()
    observer.schedule(event_handler, str(downloads_dir), recursive=False)
    observer.start()

    logger.success("Download monitoring started")

    # Get browser profile
    if profile:
        profile_dir = config.path_manager.get_cache_chrome_dir(profile)
    else:
        profile_dir = config.path_manager.get_cache_chrome_dir("system")

    profile_dir.mkdir(parents=True, exist_ok=True)

    try:
        with sync_playwright() as p:
            # Launch browser with profile
            browser = p.chromium.launch_persistent_context(
                str(profile_dir),
                headless=False,  # Always visible for manual downloads
                args=[
                    "--disable-blink-features=AutomationControlled",
                    "--disable-features=UserAgentClientHint",
                ],
            )

            # Open URLs in tabs
            if browser.pages:
                page = browser.pages[0]
            else:
                page = browser.new_page()

            if urls_to_open:
                paper_id, url = urls_to_open[0]
                page.goto(url)
                logger.success(f"[{paper_id}] {url[:80]}...")

            # Open remaining URLs
            for paper_id, url in urls_to_open[1:]:
                new_page = browser.new_page()
                new_page.goto(url)
                logger.success(f"[{paper_id}] {url[:80]}...")

            logger.info(f"\n{'=' * 60}")
            logger.info(f"Browser opened with {len(urls_to_open)} tabs")
            logger.info("Download monitoring active - PDFs will be auto-linked")
            logger.info("Use Zotero connector or save PDFs manually")
            logger.info("Press Ctrl+C when done")
            logger.info(f"{'=' * 60}\n")

            try:
                # Keep browser open
                page.wait_for_event("close", timeout=0)
            except KeyboardInterrupt:
                logger.info("\nShutting down...")
            finally:
                browser.close()

    finally:
        observer.stop()
        observer.join()
        logger.success("Download monitoring stopped")


def main():
    parser = argparse.ArgumentParser(
        description="Open browser with download monitoring and auto-linking"
    )
    parser.add_argument(
        "--project", required=True, help="Project name (e.g., neurovista, pac)"
    )
    parser.add_argument(
        "--all", action="store_true", help="Open both failed and pending PDFs"
    )
    parser.add_argument(
        "--pending", action="store_true", help="Open only pending (not attempted) PDFs"
    )
    parser.add_argument(
        "--profile", help="Browser profile name to use (default: system)"
    )
    parser.add_argument(
        "--downloads-dir",
        type=Path,
        help="Downloads directory to monitor (default: ~/Downloads)",
    )

    args = parser.parse_args()

    # Initialize config
    config = ScholarConfig()

    # Get papers based on flags
    papers = []

    if args.all or args.pending:
        pending = get_pending_papers(args.project, config)
        logger.info(f"Found {len(pending)} pending papers")
        papers.extend(pending)

    if args.all or not args.pending:
        failed = get_failed_papers(args.project, config)
        logger.info(f"Found {len(failed)} failed papers")
        papers.extend(failed)

    if not papers:
        logger.warning(f"No papers found for project: {args.project}")
        return

    # Show summary
    logger.info(f"\nOpening {len(papers)} papers with download monitoring:")
    for i, paper in enumerate(papers[:10], 1):
        title = paper.get("title", "Unknown")[:60]
        logger.info(f"  {i}. {title}...")
    if len(papers) > 10:
        logger.info(f"  ... and {len(papers) - 10} more")

    # Open browser with monitoring
    open_browser_with_monitoring(
        papers,
        args.project,
        config,
        profile=args.profile,
        downloads_dir=args.downloads_dir,
    )


if __name__ == "__main__":
    main()
