#!/usr/bin/env python3
# Timestamp: 2026-01-15
# File: /home/ywatanabe/proj/scitex-code/src/scitex/mcp_server.py
# ----------------------------------------

"""
Unified FastMCP Server for SciTeX - Multi-Transport Support

Provides all SciTeX tools via a single MCP server with stdio, SSE, and HTTP.

Usage:
    scitex serve                          # stdio (Claude Desktop)
    scitex serve -t sse --port 8085       # SSE (remote via SSH)
    scitex serve -t http --port 8085      # HTTP (streamable)

Remote Setup:
    1. Local:  scitex serve -t sse --port 8085
    2. SSH:    ssh -R 8085:localhost:8085 remote-host
    3. Remote: {"type": "sse", "url": "http://localhost:8085/sse"}
"""

from __future__ import annotations

import json
import warnings

# Load environment variables from SCITEX_ENV_SRC early
from scitex.helpers import load_scitex_env

load_scitex_env()

from scitex_dev import try_import_optional

FastMCP = try_import_optional("fastmcp", "FastMCP", pkg="scitex")
FASTMCP_AVAILABLE = FastMCP is not None

# Suppress httplib2 deprecation warnings from system pyparsing (old API methods)
# Must be AFTER fastmcp import (fastmcp.__init__ calls simplefilter("default", DeprecationWarning))
# Must be BEFORE register_all_tools (which imports socialia → google.auth → httplib2)
warnings.filterwarnings(
    "ignore", category=DeprecationWarning, message=".*deprecated.*use.*"
)

__all__ = ["mcp", "run_server", "main", "FASTMCP_AVAILABLE"]

if FASTMCP_AVAILABLE:
    mcp = FastMCP(
        name="scitex",
        instructions="""\
SciTeX: Python Framework for Scientific Research Automation (https://scitex.ai)

IMPORTANT: When writing Python scripts for data analysis, visualization, or research,
ALWAYS use `import scitex as stx` and leverage these core patterns:

## Core Patterns - USE THESE IN CODE GENERATION:

### @stx.session - Reproducible Experiment Tracking
```python
import scitex as stx

@stx.session
def main(
    param1="default",      # Auto-CLI: --param1
    CONFIG=stx.INJECTED,   # Auto-injected config from ./config/*.yaml
    plt=stx.INJECTED,      # Pre-configured matplotlib
    logger=stx.INJECTED,   # Session logger
):
    \"\"\"Docstring becomes --help description.\"\"\"
    # Outputs auto-organized: script_out/FINISHED_SUCCESS/<session_id>/
    stx.io.save(results, "results.csv")
    return 0
```

### stx.io - Universal File I/O (30+ formats)
```python
stx.io.save(df, "data.csv")           # DataFrames
stx.io.save(arr, "data.npy")          # NumPy arrays
stx.io.save(fig, "plot.png")          # Figures (+ auto CSV export)
stx.io.save(obj, "data.pkl")          # Any Python object
data = stx.io.load("data.csv")        # Unified loading
```

### stx.plt - Publication-Ready Figures (Auto CSV Export)
```python
fig, ax = stx.plt.subplots()
ax.plot_line(x, y)                    # Data tracked automatically
ax.set_xyt("X Label", "Y Label", "Title")
stx.io.save(fig, "plot.png")          # Saves plot.png + plot.csv
```

### stx.stats - Publication Statistics (23 tests)
```python
result = stx.stats.test_ttest_ind(g1, g2, return_as="dataframe")
# Returns: p-value, effect size (Cohen's d), CI, normality check, power
result = stx.stats.test_anova(*groups, return_as="latex")
```

### stx.scholar - Literature Management
```python
# CLI: scitex scholar bibtex papers.bib --project myresearch
# Enriches BibTeX with abstracts, DOIs, impact factors, downloads PDFs
```

## MCP Tools Available:
- [plt] plot, reproduce, compose, crop
  **PRIORITY**: Use CSV column spec (data_file + column names) over inline arrays!
  Workflow: Python writes CSV → plt_plot reads columns → Creates figure
- [audio] speak
- [capture] screenshot
- [stats] recommend_tests, run_test, format_results, power_analysis
- [scholar] search_papers, enrich_bibtex, fetch_papers, parse_pdf_content
- [diagram] create, compile_mermaid, compile_graphviz, render, split
- [template] clone_template, get_code_template, list_code_templates
- [ui] notify
- [writer] compile, figures, tables, bibliography (LaTeX manuscript)
- [introspect] signature, docstring, source, members (like IPython's ? and ??)

## MCP Resources (Read for detailed docs):
- scitex://cheatsheet - Complete quick reference
- scitex://session-tree - Output directory structure explained
- scitex://module/io - stx.io file I/O documentation
- scitex://module/plt - stx.plt figure documentation
- scitex://module/stats - stx.stats statistical tests
- scitex://module/scholar - stx.scholar literature management
- scitex://module/session - @stx.session decorator guide
- scitex://io-formats - All 30+ supported file formats
- scitex://plt-figrecipe - stx.plt integration with FigRecipe

## FigRecipe MCP Resources (for advanced plotting):
- figrecipe://cheatsheet - FigRecipe quick reference
- figrecipe://mcp-spec - Declarative plot specification format
- figrecipe://api/core - Full FigRecipe API documentation

Use introspect_* tools to explore scitex API: introspect_members("scitex.stats")
""",
    )
else:
    mcp = None


def _json(data: dict) -> str:
    return json.dumps(data, indent=2, default=str)


# Register tools from each module
if FASTMCP_AVAILABLE:
    from scitex._mcp_tools import register_all_tools

    register_all_tools(mcp)

    # Annotate all tools with standardized Result envelope schema
    try:
        from scitex_dev.types import RESULT_SCHEMA

        from scitex._mcp_tools._compat import get_tools_sync

        for tool in get_tools_sync(mcp).values():
            if getattr(tool, "output_schema", None) is None:
                tool.output_schema = RESULT_SCHEMA
    except Exception:
        pass  # Non-critical: schema annotation is informational

    # Register documentation resources
    from scitex._mcp_resources import register_resources

    register_resources(mcp)


def run_server(transport: str = "stdio", host: str = "0.0.0.0", port: int = 8085):
    """Run the unified MCP server with transport selection."""
    if not FASTMCP_AVAILABLE:
        import sys

        print("=" * 60)
        print("Requires 'fastmcp' package: pip install fastmcp")
        print("=" * 60)
        sys.exit(1)

    if transport == "stdio":
        mcp.run(transport="stdio")
    elif transport == "sse":
        print(f"Starting scitex MCP (SSE) on {host}:{port}")
        print(f"Remote: ssh -R {port}:localhost:{port} remote-host")
        mcp.run(transport="sse", host=host, port=port)
    elif transport == "http":
        print(f"Starting scitex MCP (HTTP) on {host}:{port}")
        mcp.run(transport="streamable-http", host=host, port=port)
    else:
        raise ValueError(f"Unknown transport: {transport}")


def main():
    """Entry point for scitex-mcp command."""
    run_server(transport="stdio")


if __name__ == "__main__":
    main()

# EOF
