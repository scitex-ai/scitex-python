#!/usr/bin/env python3
# Timestamp: 2026-01-15
# File: /home/ywatanabe/proj/scitex-code/src/scitex/_mcp_tools/__init__.py
"""FastMCP tool registration for unified server."""

from __future__ import annotations

from .audio import register_audio_tools
from .capture import register_capture_tools
from .clew import register_clew_tools
from .dataset import register_dataset_tools
from .dev import register_dev_tools
from .diagram import register_diagram_tools
from .fr import register_fr_tools
from .introspect import register_introspect_tools
from .linter import register_linter_tools
from .plt import register_plt_tools
from .project import register_project_tools
from .scholar import register_scholar_tools
from .social import register_social_tools
from .stats import register_stats_tools
from .template import register_template_tools
from .ui import register_ui_tools
from .usage import register_usage_tools
from .writer import register_writer_tools

__all__ = ["register_all_tools"]


def register_all_tools(mcp) -> None:
    """Register all module tools with the FastMCP server."""
    register_audio_tools(mcp)
    # canvas tools removed (deprecated since v2.16.0, use plt_compose)
    register_capture_tools(mcp)
    register_dataset_tools(mcp)
    register_dev_tools(mcp)
    register_diagram_tools(mcp)
    register_fr_tools(mcp)
    register_introspect_tools(mcp)
    register_linter_tools(mcp)
    register_plt_tools(mcp)
    register_project_tools(mcp)
    register_scholar_tools(mcp)
    register_social_tools(mcp)
    register_stats_tools(mcp)
    register_template_tools(mcp)
    register_ui_tools(mcp)
    register_usage_tools(mcp)
    register_clew_tools(mcp)
    register_writer_tools(mcp)


# EOF
