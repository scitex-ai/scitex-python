#!/usr/bin/env python3
# Timestamp: "2025-10-11 07:53:19 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex_repo/src/scitex/browser/core/ChromeProfileManager.py
# ----------------------------------------
from __future__ import annotations

import os

__FILE__ = "./src/scitex/browser/core/ChromeProfileManager.py"
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

__FILE__ = __file__

import subprocess
import time
from pathlib import Path
from typing import Dict, Optional

from scitex import logging
from scitex_scholar.config import ScholarConfig

logger = logging.getLogger(__name__)


class ChromeProfileManager:
    """Manages Chrome profile especially extensions for automated literature search."""

    EXTENSIONS = {
        "zotero_connector": {
            "id": "ekhagklcjbdpajgpjgmbionohlpdbjgc",
            "name": "Zotero Connector",
        },
        "lean_library": {
            "id": "hghakoefmnkhamdhenpbogkeopjlkpoa",
            "name": "Lean Library",
        },
        "popup_blocker": {
            "id": "bkkbcggnhapdmkeljlodobbkopceiche",
            "name": "Pop-up Blocker",
        },
        "accept_cookies": {
            "id": "ofpnikijgfhlmmjlpkfaifhhdonchhoi",
            "name": "Accept all cookies",
        },
        "2captcha_solver": {
            "id": "ifibfemgeogfhoebkmokieepdoobkbpo",
            "name": "2Captcha Solver",
        },
        "captcha_solver": {
            "id": "hlifkpholllijblknnmbfagnkjneagid",
            "name": "CAPTCHA Solver",
        },
    }

    AVAILABLE_PROFILE_NAMES = ["system", "extension", "auth", "stealth"]

    def __init__(self, profile_name: str, config: Optional[ScholarConfig] = None):
        self.name = self.__class__.__name__
        self.config = config or ScholarConfig()
        # Allow dynamic profile names (e.g., worker_0, worker_1) for parallel downloads
        # assert profile_name in self.AVAILABLE_PROFILE_NAMES

        self.profile_name = profile_name
        self.profile_dir = self.config.get_cache_chrome_dir(profile_name)
        logger.debug(
            f"{self.name}: profile_name={self.profile_name}, profile_dir={self.profile_dir}"
        )

    def _get_extension_statuses(self, profile_dir: Path) -> Dict[str, bool]:
        """Get detailed status of each extension."""
        status = {}
        extensions_path = profile_dir / "Default" / "Extensions"

        if not extensions_path.exists():
            return dict.fromkeys(self.EXTENSIONS, False)

        for key, ext_info in self.EXTENSIONS.items():
            ext_id = ext_info["id"]
            ext_dir = extensions_path / ext_id

            if ext_dir.exists():
                version_dirs = [d for d in ext_dir.iterdir() if d.is_dir()]
                if version_dirs:
                    latest_version = max(version_dirs, key=lambda x: x.name)
                    manifest_file = latest_version / "manifest.json"
                    status[key] = manifest_file.exists()
                else:
                    status[key] = False
            else:
                status[key] = False

        return status

    def check_extensions_installed(
        self, profile_dir: Path = None, verbose: bool = True
    ) -> bool:
        """Check installation status of all extensions from profile directory."""
        if profile_dir is None:
            profile_dir = self.profile_dir

        status = self._get_extension_statuses(profile_dir)
        installed_count = sum(status.values())

        if verbose:
            for key, ext_info in self.EXTENSIONS.items():
                ext_id = ext_info["id"]
                if not status.get(key, False):
                    logger.warning(
                        f"{self.name}: {ext_info['name']} ({ext_id}) not installed"
                    )

            all_installed = installed_count == len(self.EXTENSIONS)
            if all_installed:
                logger.debug(
                    f"{self.name}: All {installed_count}/{len(self.EXTENSIONS)} extensions installed"
                )
            else:
                logger.warning(
                    f"{self.name}: Only {installed_count}/{len(self.EXTENSIONS)} extensions installed"
                )

        return installed_count == len(self.EXTENSIONS)

    def _get_installed_extension_paths(self, profile_dir: Path) -> list[str]:
        """Get paths to installed extensions for --load-extension argument."""
        extension_paths = []
        extensions_dir = profile_dir / "Default" / "Extensions"

        if not extensions_dir.exists():
            return extension_paths

        for key, ext_info in self.EXTENSIONS.items():
            ext_id = ext_info["id"]
            ext_dir = extensions_dir / ext_id

            if ext_dir.exists():
                version_dirs = [d for d in ext_dir.iterdir() if d.is_dir()]
                if version_dirs:
                    latest_version = max(version_dirs, key=lambda x: x.name)
                    manifest_file = latest_version / "manifest.json"
                    if manifest_file.exists():
                        extension_paths.append(str(latest_version))

        return extension_paths

    def get_extension_args(self):
        """Get extension args using appropriate profile directory."""
        # profile_dir = self._get_profile_dir_with_system_handling()

        extension_paths = self._get_installed_extension_paths(self.profile_dir)

        extension_args = []
        if extension_paths:
            extensions_list = ",".join(extension_paths)
            extension_args.extend(
                [
                    f"--load-extension={extensions_list}",
                    f"--disable-extensions-except={extensions_list}",
                    "--enable-extensions",
                    "--disable-extensions-file-access-check",
                    "--disable-web-security",
                ]
            )
            logger.debug(
                f"Loading {len(extension_paths)} extensions from {self.profile_dir}"
            )

        return extension_args

    async def install_extensions_manually_if_not_installed_async(self, verbose=False):
        """Open Chrome for manual extension installation."""
        if self.check_extensions_installed(verbose=verbose):
            return True

        # Build Chrome command
        chrome_cmd = [
            "google-chrome",
            f"--user-data-dir={self.profile_dir}",
            "--enable-extensions",
            "--new-window",
            "--no-sandbox",
            "--disable-dev-shm-usage",
        ]
        chrome_cmd_str = " ".join(chrome_cmd)
        logger.info(f"Chrome command: {chrome_cmd_str}")

        # Add extension URLs
        for ext_info in self.EXTENSIONS.values():
            url = f"https://chrome.google.com/webstore/detail/{ext_info['id']}"
            chrome_cmd.append(url)

        # Set environment for WSL2
        env = os.environ.copy()
        if "WSL_DISTRO_NAME" in env and "DISPLAY" not in env:
            env["DISPLAY"] = ":0.0"

        # Try to launch Chrome
        try:
            process = subprocess.Popen(
                chrome_cmd,
                env=env,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                start_new_session=True,
            )
            logger.debug(f"Launched Chrome with PID {process.pid}")

            time.sleep(2)
            if process.poll() is not None:
                logger.error("Chrome exited immediately")
                return False

        except FileNotFoundError:
            logger.error("Chrome not found")
            return False

        print("\n" + "=" * 60)
        print("Chrome Extension Installation")
        print("=" * 60)
        print("Install extensions from the opened Chrome tabs, then press Enter")

        try:
            input("Press Enter when done...")
        except (EOFError, KeyboardInterrupt):
            pass

        time.sleep(2)

        if self.check_extensions_installed(verbose=False):
            logger.success("Extension installation complete!")
            return True
        else:
            logger.warning("Extension installation may be incomplete")
            return False

    async def handle_runtime_extension_dialogs_async(self, page):
        """Handle extension consent dialogs that appear at runtime."""
        try:
            await page.wait_for_timeout(2000)

            consent_selectors = [
                'button:has-text("Agree")',
                'button:has-text("Accept")',
                'button:has-text("Continue")',
                'button:has-text("OK")',
                'button:has-text("Dismiss")',
                'button:has-text("Close")',
            ]

            for selector in consent_selectors:
                element = await page.query_selector(selector)
                if element:
                    await element.click()
                    logger.debug(f"Clicked dialog: {selector}")
                    return True

            return False

        except Exception as e:
            logger.error(f"Error handling dialogs: {e}")
            return False

    def sync_from_profile(self, source_profile_name: str = "system") -> bool:
        """
        Sync extensions and cookies from source profile to this profile using rsync.

        Args:
            source_profile_name: Name of source profile (default: "system")

        Returns
        -------
            True if sync succeeded, False otherwise
        """
        import time

        source_profile_dir = self.config.get_cache_chrome_dir(source_profile_name)

        if not source_profile_dir.exists():
            logger.error(f"Source profile does not exist: {source_profile_dir}")
            return False

        # Create target profile directory if needed
        self.profile_dir.mkdir(parents=True, exist_ok=True)

        logger.debug(f"Syncing profile: {self.profile_name} ← {source_profile_name}")
        logger.debug(f"  Source: {source_profile_dir}")
        logger.debug(f"  Target: {self.profile_dir}")

        # Use rsync to sync entire profile directory
        # -a: archive mode (preserves permissions, timestamps, symlinks)
        # -u: skip files newer on receiver
        # -v: verbose output
        # --stats: show transfer statistics
        # --delete: delete files not in source (keep profiles identical)
        rsync_cmd = [
            "rsync",
            "-auv",
            "--stats",
            "--delete",
            f"{source_profile_dir}/",
            f"{self.profile_dir}/",
        ]

        start_time = time.time()

        try:
            result = subprocess.run(
                rsync_cmd, capture_output=True, text=True, check=True
            )

            elapsed = time.time() - start_time

            # Parse rsync stats
            stats_lines = result.stdout.strip().split("\n")
            transferred_files = 0
            total_size = 0

            for line in stats_lines:
                if "Number of regular files transferred:" in line:
                    # Remove commas from number (e.g., "3,301" -> "3301")
                    transferred_files = int(line.split(":")[1].strip().replace(",", ""))
                elif "Total transferred file size:" in line:
                    size_str = line.split(":")[1].strip().split()[0]
                    total_size = int(size_str.replace(",", ""))

            # Log detailed results
            if transferred_files > 0:
                size_mb = total_size / (1024 * 1024)
                logger.success(
                    f"Profile sync complete: {self.profile_name} ← {source_profile_name} "
                    f"({transferred_files} files, {size_mb:.1f}MB, {elapsed:.2f}s)"
                )
            else:
                logger.debug(
                    f"Profile sync complete: {self.profile_name} ← {source_profile_name} "
                    f"(no changes, {elapsed:.2f}s)"
                )

            # Log verbose output at debug level
            if result.stdout:
                logger.debug(f"rsync output:\n{result.stdout}")

            return True

        except subprocess.CalledProcessError as e:
            # Exit code 23 = partial transfer (often just timestamp issues on WSL)
            # Check if it's only "failed to set times" errors - these are harmless
            if e.returncode == 23 and "failed to set times" in e.stderr:
                # Files copied successfully, just couldn't preserve timestamps
                logger.debug("Profile sync complete (timestamps not preserved)")
                return True
            logger.error(f"rsync failed (exit code {e.returncode}): {e.stderr}")
            return False
        except FileNotFoundError:
            logger.error("rsync command not found - please install rsync")
            return False


def main(args):
    """Demonstrate ChromeProfileManager functionality."""
    import asyncio

    async def demo():
        manager = ChromeProfileManager("system")

        # Check extensions
        print("Checking system profile extensions...")
        all_installed = manager.check_extensions_installed(verbose=True)

        if not all_installed:
            print("\nInstalling missing extensions...")
            await manager.install_extensions_manually_if_not_installed_async(
                verbose=True
            )

        # Demo profile sync
        print("\nChecking profile sync capability...")
        test_profile = ChromeProfileManager("test_profile")
        success = test_profile.sync_from_profile("system")
        if success:
            print("✓ Profile sync test complete")
        else:
            print("✓ Profile sync skipped (source profile not ready)")

        print("✓ Demo complete")

    asyncio.run(demo())
    return 0


def parse_args():
    """Parse command line arguments."""
    import argparse

    parser = argparse.ArgumentParser(description="ChromeProfileManager demo")
    return parser.parse_args()


def run_main() -> None:
    """Initialize scitex framework, run main function, and cleanup."""
    global CONFIG, CC, sys, plt, rng

    import sys

    import matplotlib.pyplot as plt

    import scitex as stx

    args = parse_args()

    CONFIG, sys.stdout, sys.stderr, plt, CC, rng = stx.session.start(
        sys,
        plt,
        args=args,
        file=__FILE__,
        sdir_suffix=None,
        verbose=False,
        agg=True,
    )

    exit_status = main(args)

    stx.session.close(
        CONFIG,
        verbose=False,
        notify=False,
        message="",
        exit_status=exit_status,
    )


if __name__ == "__main__":
    run_main()

# python -m scitex.browser.core.ChromeProfileManager

# EOF
