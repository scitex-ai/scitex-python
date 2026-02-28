#!/usr/bin/env python3
# Timestamp: 2026-01-15
# File: /home/ywatanabe/proj/scitex-code/src/scitex/_mcp_tools/__init__.py
"""FastMCP tool registration for unified server."""

from .audio import register_audio_tools
from .capture import register_capture_tools
from .clew import register_clew_tools
from .cloud import register_cloud_tools
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
from .tunnel import register_tunnel_tools
from .ui import register_ui_tools
from .usage import register_usage_tools
from .writer import register_writer_tools

__all__ = ["register_all_tools"]

# Map: env var suffix → registration function
_TOOL_GROUPS = {
    "AUDIO": register_audio_tools,
    "CAPTURE": register_capture_tools,
    "CLEW": register_clew_tools,
    "CLOUD": register_cloud_tools,
    "DATASET": register_dataset_tools,
    "DEV": register_dev_tools,
    "DIAGRAM": register_diagram_tools,
    "FR": register_fr_tools,
    "INTROSPECT": register_introspect_tools,
    "LINTER": register_linter_tools,
    "PLT": register_plt_tools,
    "PROJECT": register_project_tools,
    "SCHOLAR": register_scholar_tools,
    "SOCIAL": register_social_tools,
    "STATS": register_stats_tools,
    "TEMPLATE": register_template_tools,
    "TUNNEL": register_tunnel_tools,
    "UI": register_ui_tools,
    "USAGE": register_usage_tools,
    "WRITER": register_writer_tools,
}


def _is_enabled(group: str) -> bool:
    """Check SCITEX_MCP_USE_<GROUP> env var. Default: enabled (1)."""
    import os

    return os.environ.get(f"SCITEX_MCP_USE_{group}", "1") != "0"


def register_all_tools(mcp) -> None:
    """Register module tools with the FastMCP server.

    Each group is gated by SCITEX_MCP_USE_<GROUP> env var (default: 1).
    Set to 0 to disable. See .env.d.examples/02_mcp.env.
    """
    for group, register_fn in _TOOL_GROUPS.items():
        if _is_enabled(group):
            register_fn(mcp)


# EOF
