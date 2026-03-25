---
description: Command-line interface for stx.capture — take screenshots, list windows, start/stop monitoring, create GIFs, and launch the MCP server.
---

# cli — Command-Line Interface

Entry point: `python -m scitex.capture` (defined in `capture/__main__.py` and
`capture/cli.py`).

## Usage

```
python -m scitex.capture [message] [options]
```

## Arguments and Flags

| Flag | Type | Description |
|------|------|-------------|
| `message` | positional (optional) | Label embedded in filename |
| `--all` | flag | Capture all monitors |
| `--app APP` | str | Capture named app window (e.g. `chrome`) |
| `--url URL` | str | Capture URL via browser |
| `--monitor N` | int (default 0) | Monitor index (0-based) |
| `--quality N` | int (default 85) | JPEG quality 1-100 |
| `-o / --output PATH` | str | Explicit output path |
| `--list` | flag | List visible windows |
| `--info` | flag | Show monitor/virtual-desktop info |
| `--start` | flag | Start continuous monitoring |
| `--stop` | flag | Stop continuous monitoring |
| `--gif` | flag | Create GIF from latest session |
| `--mcp` | flag | Start MCP server |
| `--interval SEC` | float (default 1.0) | Monitoring interval |
| `-q / --quiet` | flag | Suppress output |

## Examples

```bash
# Single screenshot, primary monitor
python -m scitex.capture

# With label
python -m scitex.capture "after_training"

# All monitors
python -m scitex.capture --all

# Specific monitor
python -m scitex.capture --monitor 1

# Capture Chrome
python -m scitex.capture --app chrome

# Capture a local web server
python -m scitex.capture --url 127.0.0.1:8000

# Save to specific path
python -m scitex.capture -o /tmp/debug.jpg

# List visible windows (handle + process name)
python -m scitex.capture --list

# Show monitor info
python -m scitex.capture --info

# Start monitoring at 2-second intervals
python -m scitex.capture --start --interval 2.0

# Stop monitoring (sends stop signal to running session)
python -m scitex.capture --stop

# Create GIF from the latest monitoring session
python -m scitex.capture --gif

# Start unified MCP server
python -m scitex.capture --mcp
```

## Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Success |
| 1 | Screenshot failed or other error |
| 130 | Interrupted by Ctrl+C |

## --start behaviour

`--start` runs an infinite loop (`time.sleep(1)`) until `KeyboardInterrupt`,
then calls `capture.stop()` automatically. The captures are saved to
`~/.scitex/capture/`.

## --mcp behaviour

Prints the JSON snippet for adding `scitex-capture` to Claude Code's MCP
server config, then launches the async MCP server via `asyncio.run(mcp_main())`.
Note: the standalone `mcp_server.py` is deprecated; the unified scitex MCP
server (`scitex serve`) is preferred.
