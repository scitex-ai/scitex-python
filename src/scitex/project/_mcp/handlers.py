#!/usr/bin/env python3
# Timestamp: 2026-02-19
# File: scitex/project/_mcp/handlers.py
"""
Project file operation handlers for MCP tools.

Security: all operations are constrained to paths under ALLOWED_DATA_ROOT.
Path traversal (../) is blocked at resolution time.
"""

from __future__ import annotations

import fnmatch
import os
from pathlib import Path
from typing import Any

# Configurable via environment — default matches Docker container layout
ALLOWED_DATA_ROOT = os.environ.get("SCITEX_PROJECT_DATA_ROOT", "/app/data/users")


def _resolve_safe(root_path: str, relative_path: str = "") -> Path:
    """
    Resolve a path within root_path, raising ValueError on any violation.

    Checks:
    1. root_path must be under ALLOWED_DATA_ROOT
    2. Resolved target must be under root_path (no path traversal)
    """
    root = Path(root_path).resolve()
    allowed = Path(ALLOWED_DATA_ROOT).resolve()

    if not str(root).startswith(str(allowed)):
        raise ValueError(
            f"root_path '{root}' is not under allowed data root '{allowed}'. "
            "Project paths must be within the configured data directory."
        )

    if relative_path and relative_path not in (".", ""):
        target = (root / relative_path).resolve()
    else:
        target = root

    if not str(target).startswith(str(root)):
        raise ValueError(
            f"Path traversal detected: '{relative_path}' escapes project root."
        )

    return target


def _build_tree(path: Path, max_depth: int, current_depth: int = 0) -> list[dict]:
    """Recursively build a file tree structure."""
    if current_depth >= max_depth:
        return []

    entries = []
    try:
        items = sorted(path.iterdir(), key=lambda p: (p.is_file(), p.name))
    except PermissionError:
        return []

    for item in items:
        # Skip hidden files/dirs and common noise
        if item.name.startswith(".") or item.name in (
            "__pycache__",
            "node_modules",
            ".git",
        ):
            continue
        entry: dict[str, Any] = {
            "name": item.name,
            "type": "file" if item.is_file() else "dir",
        }
        if item.is_dir():
            entry["children"] = _build_tree(item, max_depth, current_depth + 1)
        else:
            entry["size"] = item.stat().st_size
        entries.append(entry)

    return entries


async def list_files_handler(
    root_path: str,
    relative_path: str = ".",
    max_depth: int = 3,
) -> dict:
    """List files and directories within the project."""
    try:
        target = _resolve_safe(root_path, relative_path)
    except ValueError as e:
        return {"success": False, "error": str(e)}

    if not target.exists():
        return {"success": False, "error": f"Path does not exist: {relative_path}"}
    if not target.is_dir():
        return {"success": False, "error": f"Not a directory: {relative_path}"}

    tree = _build_tree(target, max_depth=max(1, min(max_depth, 6)))
    return {
        "success": True,
        "path": str(target.relative_to(Path(root_path).resolve())),
        "tree": tree,
    }


async def read_file_handler(
    root_path: str,
    relative_path: str,
    max_bytes: int = 65536,
) -> dict:
    """Read file content from the project."""
    try:
        target = _resolve_safe(root_path, relative_path)
    except ValueError as e:
        return {"success": False, "error": str(e)}

    if not target.exists():
        return {"success": False, "error": f"File not found: {relative_path}"}
    if not target.is_file():
        return {"success": False, "error": f"Not a file: {relative_path}"}

    size = target.stat().st_size
    truncated = size > max_bytes

    try:
        with open(target, encoding="utf-8", errors="replace") as f:
            content = f.read(max_bytes)
    except Exception as e:
        return {"success": False, "error": f"Cannot read file: {e}"}

    return {
        "success": True,
        "path": relative_path,
        "content": content,
        "size_bytes": size,
        "truncated": truncated,
        "truncated_at_bytes": max_bytes if truncated else None,
    }


async def write_file_handler(
    root_path: str,
    relative_path: str,
    content: str,
) -> dict:
    """Write content to a file in the project (creates parent dirs as needed)."""
    try:
        target = _resolve_safe(root_path, relative_path)
    except ValueError as e:
        return {"success": False, "error": str(e)}

    try:
        target.parent.mkdir(parents=True, exist_ok=True)
        with open(target, "w", encoding="utf-8") as f:
            f.write(content)
    except Exception as e:
        return {"success": False, "error": f"Cannot write file: {e}"}

    return {
        "success": True,
        "path": relative_path,
        "size_bytes": target.stat().st_size,
    }


async def search_files_handler(
    root_path: str,
    name_pattern: str = "",
    content_pattern: str = "",
    relative_path: str = ".",
    max_results: int = 50,
) -> dict:
    """Search project files by name glob and/or content substring."""
    try:
        search_root = _resolve_safe(root_path, relative_path)
    except ValueError as e:
        return {"success": False, "error": str(e)}

    if not search_root.exists():
        return {"success": False, "error": f"Directory not found: {relative_path}"}

    if not name_pattern and not content_pattern:
        return {"success": False, "error": "Provide name_pattern or content_pattern"}

    matches = []
    root_resolved = Path(root_path).resolve()

    for item in search_root.rglob("*"):
        if len(matches) >= max_results:
            break
        # Skip hidden and noisy items — check relative path only, not absolute prefix
        rel_parts = item.relative_to(search_root).parts
        if any(
            p.startswith(".") or p in ("__pycache__", "node_modules") for p in rel_parts
        ):
            continue
        if not item.is_file():
            continue

        name_ok = not name_pattern or fnmatch.fnmatch(item.name, name_pattern)
        if not name_ok:
            continue

        if content_pattern:
            try:
                text = item.read_text(encoding="utf-8", errors="replace")
                if content_pattern not in text:
                    continue
                # Find first matching line for context
                for lineno, line in enumerate(text.splitlines(), 1):
                    if content_pattern in line:
                        match_line = lineno
                        match_preview = line.strip()[:120]
                        break
                else:
                    match_line, match_preview = 0, ""
            except Exception:
                continue
            matches.append(
                {
                    "path": str(item.relative_to(root_resolved)),
                    "line": match_line,
                    "preview": match_preview,
                }
            )
        else:
            matches.append({"path": str(item.relative_to(root_resolved))})

    return {
        "success": True,
        "matches": matches,
        "count": len(matches),
        "truncated": len(matches) >= max_results,
    }


# EOF
