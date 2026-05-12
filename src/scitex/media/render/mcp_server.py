#!/usr/bin/env python3
"""MCP tools for scitex.media.render — thin wrappers around Python API."""

from __future__ import annotations

import json
from typing import Optional

from scitex_dev import try_import_optional

FastMCP = try_import_optional("fastmcp", "FastMCP", pkg="scitex")
FASTMCP_AVAILABLE = FastMCP is not None

__all__ = ["mcp", "FASTMCP_AVAILABLE"]

if FASTMCP_AVAILABLE:
    mcp = FastMCP(
        name="scitex-media-render",
        instructions=(
            "Media rendering tools for SciTeX. "
            "Detect, classify, and display media files in chat, terminal, or markdown."
        ),
    )

    @mcp.tool()
    def render_show(
        path: str,
        target: str = "terminal",
        root_path: Optional[str] = None,
        alt: str = "",
    ) -> str:
        """Display a media file in the specified target.

        Args:
            path: File path to display.
            target: "terminal" (OSC overlay), "chat" (inline dict), "markdown" (embed).
            root_path: Project root for chat target (makes path relative).
            alt: Alt text for markdown images.
        """
        from . import show

        return show(path, target=target, root_path=root_path, alt=alt)

    @mcp.tool()
    def render_detect(text: str, root_path: Optional[str] = None) -> str:
        """Detect media file references in text.

        Args:
            text: Text containing file paths.
            root_path: Project root to match against.
        """
        from . import detect

        return json.dumps(detect(text, root_path=root_path), indent=2)

    @mcp.tool()
    def render_classify(path: str) -> str:
        """Classify a file by media type.

        Args:
            path: File path to classify.
        """
        from . import classify

        ref = classify(path)
        return json.dumps(ref, indent=2) if ref else "null"

else:
    mcp = None


def main():
    """Entry point for MCP server."""
    if not FASTMCP_AVAILABLE:
        import sys

        print("MCP server requires fastmcp: pip install fastmcp")
        sys.exit(1)
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()

# EOF
