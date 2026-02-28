#!/usr/bin/env python3
# File: /home/ywatanabe/proj/scitex-code/src/scitex/git/remote.py

"""
Git remote operations.
"""

from pathlib import Path
from typing import Optional

from scitex.logging import getLogger
from scitex.sh import sh

from ._constants import EXIT_FAILURE, EXIT_SUCCESS
from ._utils import _in_directory

logger = getLogger(__name__)


def get_remote_url(
    repo_path: Path, remote_name: str = "origin", verbose: bool = False
) -> Optional[str]:
    """
    Get remote URL for a git repository.

    Parameters
    ----------
    repo_path : Path
        Git repository path
    remote_name : str
        Remote name (default: origin)
    verbose : bool
        Enable verbose output

    Returns
    -------
    Optional[str]
        Remote URL if found, None otherwise

    Notes
    -----
    Returns None if remote doesn't exist or repo is not a git repository.
    Check stderr via sh() directly if detailed error info is needed.
    """
    if not (repo_path / ".git").exists():
        logger.warning(f"Not a git repository: {repo_path}")
        return None

    with _in_directory(repo_path):
        result = sh(
            ["git", "config", "--get", f"remote.{remote_name}.url"],
            verbose=verbose,
            return_as="dict",
        )
        if result["success"]:
            return result["stdout"].strip()

        logger.debug(f"Remote '{remote_name}' not found in {repo_path}")
        return None


def _validate_git_url(url: str) -> bool:
    """
    Validate git URL format.

    Parameters
    ----------
    url : str
        Git URL to validate

    Returns
    -------
    bool
        True if valid, False otherwise
    """
    valid_hosts = ("github.com", "gitlab.com", "bitbucket.org")

    if url.startswith("https://"):
        for host in valid_hosts:
            if f"https://{host}/" in url:
                return True

    elif url.startswith("git@"):
        for host in valid_hosts:
            if url.startswith(f"git@{host}:"):
                return True

    return False


def _normalize_git_url(url: str) -> str:
    """
    Normalize git URL for comparison.
    Handles HTTPS and SSH formats for GitHub, GitLab, Bitbucket.

    Parameters
    ----------
    url : str
        Git URL to normalize

    Returns
    -------
    str
        Normalized URL
    """
    url = url.rstrip("/")

    if url.startswith("git@"):
        url = url.replace(":", "/", 1).replace("git@", "https://")

    if url.endswith(".git"):
        url = url[:-4]

    return url


def is_cloned_from(
    repo_path: Path, expected_url: str, remote_name: str = "origin"
) -> bool:
    """
    Check if directory is a git repository cloned from specific URL.
    Handles both HTTPS and SSH URL formats.

    Parameters
    ----------
    repo_path : Path
        Directory to check
    expected_url : str
        Expected remote URL
    remote_name : str
        Remote name to check (default: origin)

    Returns
    -------
    bool
        True if directory is cloned from expected URL, False otherwise
    """
    if not (repo_path / ".git").exists():
        return False
    actual_url = get_remote_url(repo_path, remote_name)
    if actual_url is None:
        return False
    return _normalize_git_url(actual_url) == _normalize_git_url(expected_url)


def ls_remote(
    url: str,
    ref: Optional[str] = None,
    verbose: bool = False,
) -> Optional[str]:
    """
    Get commit hash of a remote ref via ``git ls-remote``.

    Parameters
    ----------
    url : str
        Git repository URL.
    ref : str, optional
        Branch name, tag, or ref pattern. If None, returns HEAD.
    verbose : bool
        Enable verbose output.

    Returns
    -------
    Optional[str]
        Commit SHA-1 hash (40 hex chars), or None on failure.

    Examples
    --------
    >>> ls_remote("https://github.com/user/repo.git")
    'abc123...'
    >>> ls_remote("https://github.com/user/repo.git", ref="main")
    'abc123...'
    >>> ls_remote("https://github.com/user/repo.git", ref="v1.0.0")
    'def456...'
    """
    cmd = ["git", "ls-remote"]
    if ref is None:
        cmd.append("--symref")
    cmd.append(url)
    if ref is not None:
        cmd.append(ref)

    result = sh(cmd, verbose=verbose, return_as="dict")
    if not result["success"]:
        logger.debug(f"ls-remote failed for {url}: {result.get('stderr', '')}")
        return None

    stdout = result["stdout"].strip()
    if not stdout:
        return None

    # Parse first line: "<hash>\t<ref>"
    for line in stdout.splitlines():
        parts = line.split("\t", 1)
        if len(parts) == 2 and len(parts[0]) == 40:
            return parts[0]

    return None


def get_head_hash(
    repo_path: Path,
    verbose: bool = False,
) -> Optional[str]:
    """
    Get HEAD commit hash of a local git repository.

    Parameters
    ----------
    repo_path : Path
        Git repository path (must contain .git/).
    verbose : bool
        Enable verbose output.

    Returns
    -------
    Optional[str]
        Commit SHA-1 hash, or None if not a git repo.
    """
    if not (repo_path / ".git").exists():
        return None

    with _in_directory(repo_path):
        result = sh(
            ["git", "rev-parse", "HEAD"],
            verbose=verbose,
            return_as="dict",
        )
        if result["success"]:
            return result["stdout"].strip()
        return None


def main(args):
    if args.action == "get-url":
        url = get_remote_url(args.repo_path, args.remote_name, args.verbose)
        if url:
            print(url)
            return EXIT_SUCCESS
        return EXIT_FAILURE
    elif args.action == "check-origin":
        if not args.expected_url:
            logger.error("Expected URL required for check-origin action")
            return EXIT_FAILURE
        result = is_cloned_from(args.repo_path, args.expected_url, args.remote_name)
        print(result)
        return EXIT_SUCCESS if result else EXIT_FAILURE


def parse_args():
    """Parse command line arguments."""
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--action", choices=["get-url", "check-origin"], required=True)
    parser.add_argument("--repo-path", type=Path, required=True)
    parser.add_argument("--expected-url", help="Expected URL for check-origin action")
    parser.add_argument("--remote-name", default="origin")
    parser.add_argument("--verbose", action="store_true")
    return parser.parse_args()


def run_session():
    """Initialize scitex framework, run main function, and cleanup."""
    from ._session import run_with_session

    run_with_session(parse_args, main)


__all__ = [
    "get_remote_url",
    "is_cloned_from",
    "ls_remote",
    "get_head_hash",
    "_validate_git_url",
]


if __name__ == "__main__":
    run_session()

# EOF
