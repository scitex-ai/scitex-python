#!/usr/bin/env python3
# Timestamp: 2026-01-29
# File: src/scitex/_mcp_tools/canvas.py
"""Canvas module tools for FastMCP unified server.

.. deprecated:: 2.16.0
    Canvas tools are deprecated. Use figrecipe MCP tools instead:
    - plt_compose for multi-panel composition
    - plt_plot for creating figures
    - plt_reproduce for reproducing from recipes

    figrecipe is mounted automatically if installed.
"""


def register_canvas_tools(mcp) -> None:
    """Register canvas tools with FastMCP server.

    Note: These tools are deprecated. Use plt_compose from figrecipe instead.
    plt_* and diagram_* tools are registered via plt.py and diagram.py respectively.
    """

    # Legacy canvas tools only (deprecated, for backward compatibility)
    # plt_* tools are registered in plt.py, diagram_* in diagram.py
    @mcp.tool()
    async def canvas_create_canvas(
        parent_dir: str,
        canvas_name: str,
        width_mm: float = 180,
        height_mm: float = 120,
    ) -> str:
        """[DEPRECATED]Create a canvas workspace. Use plt_compose instead."""
        from scitex.canvas._mcp.handlers import create_canvas_handler

        result = await create_canvas_handler(
            parent_dir=parent_dir,
            canvas_name=canvas_name,
            width_mm=width_mm,
            height_mm=height_mm,
        )
        result["_deprecated"] = "Use plt_compose from figrecipe instead"
        from scitex_dev.types import Result

        return Result(success=True, data=result).to_json()

    @mcp.tool()
    async def canvas_add_panel(
        parent_dir: str,
        canvas_name: str,
        panel_name: str,
        source: str,
        x_mm: float = 0,
        y_mm: float = 0,
        width_mm: float = 50,
        height_mm: float = 50,
        label: str | None = None,
    ) -> str:
        """[DEPRECATED]Add a panel to canvas. Use plt_compose instead."""
        from scitex.canvas._mcp.handlers import add_panel_handler

        result = await add_panel_handler(
            parent_dir=parent_dir,
            canvas_name=canvas_name,
            panel_name=panel_name,
            source=source,
            x_mm=x_mm,
            y_mm=y_mm,
            width_mm=width_mm,
            height_mm=height_mm,
            label=label,
        )
        result["_deprecated"] = "Use plt_compose from figrecipe instead"
        from scitex_dev.types import Result

        return Result(success=True, data=result).to_json()

    @mcp.tool()
    async def canvas_list_panels(parent_dir: str, canvas_name: str) -> str:
        """[DEPRECATED]List panels in a canvas."""
        from scitex.canvas._mcp.handlers import list_panels_handler

        result = await list_panels_handler(
            parent_dir=parent_dir, canvas_name=canvas_name
        )
        result["_deprecated"] = "Use figrecipe instead"
        from scitex_dev.types import Result

        return Result(success=True, data=result).to_json()

    @mcp.tool()
    async def canvas_remove_panel(
        parent_dir: str, canvas_name: str, panel_name: str
    ) -> str:
        """[DEPRECATED]Remove a panel from canvas."""
        from scitex.canvas._mcp.handlers import remove_panel_handler

        result = await remove_panel_handler(
            parent_dir=parent_dir,
            canvas_name=canvas_name,
            panel_name=panel_name,
        )
        result["_deprecated"] = "Use figrecipe instead"
        from scitex_dev.types import Result

        return Result(success=True, data=result).to_json()

    @mcp.tool()
    async def canvas_export_canvas(
        parent_dir: str,
        canvas_name: str,
        output_path: str | None = None,
        format: str | None = None,
        dpi: int = 300,
    ) -> str:
        """[DEPRECATED]Export canvas to image. Use plt_compose instead."""
        from scitex.canvas._mcp.handlers import export_canvas_handler

        result = await export_canvas_handler(
            parent_dir=parent_dir,
            canvas_name=canvas_name,
            output_path=output_path,
            format=format,
            dpi=dpi,
        )
        result["_deprecated"] = "Use plt_compose from figrecipe instead"
        from scitex_dev.types import Result

        return Result(success=True, data=result).to_json()

    @mcp.tool()
    async def canvas_list_canvases(parent_dir: str) -> str:
        """[DEPRECATED]List canvases in a directory."""
        from scitex.canvas._mcp.handlers import list_canvases_handler

        result = await list_canvases_handler(parent_dir=parent_dir)
        result["_deprecated"] = "Use figrecipe instead"
        from scitex_dev.types import Result

        return Result(success=True, data=result).to_json()

    @mcp.tool()
    async def canvas_canvas_exists(parent_dir: str, canvas_name: str) -> str:
        """[DEPRECATED]Check if a canvas exists."""
        from scitex.canvas._mcp.handlers import canvas_exists_handler

        result = await canvas_exists_handler(
            parent_dir=parent_dir, canvas_name=canvas_name
        )
        result["_deprecated"] = "Use figrecipe instead"
        from scitex_dev.types import Result

        return Result(success=True, data=result).to_json()


# EOF
