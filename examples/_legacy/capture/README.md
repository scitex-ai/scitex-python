# Scitex Capture Examples

Examples demonstrating the `scitex.capture` module, which provides screen capture and monitoring capabilities through cammy MCP integration.

## Prerequisites

1. Ensure cammy MCP server is installed and configured
2. Install scitex with capture dependencies

## Examples

### 1. basic_usage.py

Demonstrates core functionality:
- Single screenshots
- Application window capture
- Continuous monitoring
- GIF creation from sessions
- Window enumeration and capture
- System information retrieval
- Cache management

Run:
```bash
python basic_usage.py
```

### 2. debugging_workflow.py

Shows practical debugging scenarios:
- Browser automation with step-by-step screenshots
- Long-running process monitoring
- Timeline GIF creation for review
- Error state capture
- Recent captures analysis

Run:
```bash
python debugging_workflow.py
```

## Common Use Cases

### Quick Debug Screenshot
```python
from scitex import capture
path = capture.screenshot(message="debug_point_1")
print(f"Saved to: {path}")
```

### Monitor Process
```python
from scitex import capture
import time

# Start monitoring
capture.start_monitoring(interval=1.0)

# Do your work
time.sleep(10)

# Stop and create review GIF
capture.stop_monitoring()
gif = capture.create_gif(session_id="latest")
```

### Capture Application Window
```python
from scitex import capture

# Capture Chrome browser
path = capture.screenshot(app="chrome", message="browser_state")
```

### Review Timeline
```python
from scitex import capture

# List recent screenshots
recent = capture.list_recent(limit=10)
for path in recent:
    print(path)

# Create GIF summary
gif = capture.create_gif(session_id="latest", duration=0.5)
```

## Configuration

Default settings can be customized in `config/capture.yaml`:
- Screenshot quality
- Monitoring interval
- Output directories
- GIF creation options
- Cache management

## Tips

1. Use meaningful message strings for easy identification later
2. Lower quality (60) for continuous monitoring to save space
3. Higher quality (85-95) for detailed debugging screenshots
4. Create GIFs to review process flow
5. Use cache management to keep disk usage under control

## Notes

- Screenshots are saved to `~/.cache/cammy` by default
- Monitoring creates timestamped sessions for easy GIF creation
- All functions include proper error handling and logging

EOF
