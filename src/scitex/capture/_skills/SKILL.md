---
name: stx.capture
description: AI-optimized screen capture for WSL/Windows — single shots, multi-monitor, URL, app window, continuous monitoring, GIF creation, and grid overlays.
---

# stx.capture

Lightweight screen capture module optimized for WSL and Windows environments.
Captures the Windows host screen from inside WSL via PowerShell scripts.

## Sub-skills

- [snap.md](snap.md) — Single screenshot: `capture()` / `snap()`, auto-categorize, URL, app, all-monitors
- [monitor.md](monitor.md) — Continuous monitoring: `start_monitor()` / `stop_monitor()`, `Session` context manager
- [gif.md](gif.md) — GIF creation from session frames or arbitrary image lists
- [display-info.md](display-info.md) — `get_info()`, `capture_window()`, window enumeration
- [grid.md](grid.md) — Grid/cursor/monitor overlays for coordinate debugging
- [cli.md](cli.md) — `python -m scitex.capture` command-line interface
- [mcp.md](mcp.md) — MCP tools exposed via the unified scitex MCP server
