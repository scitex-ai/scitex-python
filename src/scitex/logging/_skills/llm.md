---
name: logging-llm
description: stx.logging.llm — parse, render, and analyze Claude Code JSONL session logs. Includes HTML rendering, DAG visualization, action extraction, script export, and multi-session dashboard.
---

# LLM Session Logs

`stx.logging.llm` parses Claude Code JSONL session files into structured Python objects, and provides tools for visualization, reproducibility, and analysis.

## Quick start

```python
import scitex as stx

session = stx.logging.llm.load("~/.claude/projects/xxx/session.jsonl")
print(session.summary())        # token counts, tool usage, duration
session.render("session.html")  # self-contained HTML viewer
print(session.to_dag())         # {"nodes": [...], "edges": [...]}
```

## load()

```python
stx.logging.llm.load(path) -> ClaudeCodeSession
```

Reads a `.jsonl` file and returns a `ClaudeCodeSession`. Accepts `str` or `Path`; expands `~`.

## ClaudeCodeSession

```python
@dataclass
class ClaudeCodeSession:
    path: Path
    session_id: str
    slug: str
    entries: list[Entry]
    version: str
    git_branch: str
```

**Properties**

| Property | Type | Description |
|----------|------|-------------|
| `.user_entries` | list[Entry] | Entries where `type == "user"` |
| `.assistant_entries` | list[Entry] | Entries where `type == "assistant"` |
| `.tool_calls` | list[ToolCall] | All tool calls across all entries |
| `.total_input_tokens` | int | Sum of input tokens across all entries |
| `.total_output_tokens` | int | Sum of output tokens across all entries |
| `.total_tokens` | int | `total_input_tokens + total_output_tokens` |

**Methods**

```python
session.summary() -> dict    # statistics dict (see below)
session.render(output)       # write HTML, return Path
session.to_dag() -> dict     # {"nodes": [...], "edges": [...]}
```

**summary() keys**

`session_id`, `slug`, `version`, `git_branch`, `total_entries`, `user_turns`, `assistant_turns`, `total_tool_calls`, `tool_usage` (dict sorted by count descending), `total_input_tokens`, `total_output_tokens`, `total_tokens`, `total_duration_ms`

## Entry, ToolCall, ToolResult

```python
@dataclass
class Entry:
    type: str           # "user", "assistant", "system"
    uuid: str
    parent_uuid: str
    timestamp: str
    role: str           # "user" or "assistant"
    text: str
    tool_calls: list[ToolCall]
    tool_result: Optional[ToolResult]
    model: str
    input_tokens: int
    output_tokens: int
    cache_creation_tokens: int
    cache_read_tokens: int
    duration_ms: int

@dataclass
class ToolCall:
    id: str
    name: str
    input: dict
    timestamp: Optional[str]

@dataclass
class ToolResult:
    tool_use_id: str
    stdout: str
    stderr: str
    interrupted: bool
    is_image: bool
```

## Action extraction

An `Action` pairs a `ToolCall` with its `ToolResult` for reproducibility analysis.

```python
actions = stx.logging.llm.extract_actions(path) -> list[Action]
```

```python
@dataclass
class Action:
    tool_name: str
    tool_input: dict
    tool_use_id: str
    timestamp: str
    result_content: str
    stdout: str
    stderr: str
    exit_code: Optional[int]
    interrupted: bool
    is_image: bool
```

**Action convenience properties**

| Property | Description |
|----------|-------------|
| `.command` | `tool_input["command"]` for Bash tools |
| `.file_path` | `tool_input["file_path"]` for Read/Write/Edit |
| `.description` | `tool_input["description"]` |

**Format actions as text or JSONL**

```python
log_text = stx.logging.llm.actions_to_log(actions, max_output=3000)
jsonl_text = stx.logging.llm.actions_to_jsonl(actions)
```

## DAG

```python
dag = stx.logging.llm.build_dag(session) -> {"nodes": [...], "edges": [...]}
# Each node: {"id": str, "name": str, "timestamp": str}
# Each edge: {"from": str, "to": str}

mermaid_src = stx.logging.llm.to_mermaid(session) -> str
```

Sequential tool calls are connected; cross-turn edges connect last call of one turn to first of the next.

## Rendering

```python
# Single session HTML
session.render("./session.html")  # or:
# stx.logging.llm renders via _renderer.render_html internally

# Multi-session dashboard
stx.logging.llm.render_dashboard(
    output="/tmp/claude_dashboard.html",
    claude_dir="~/.claude",
)

# Single-page application with session switching
stx.logging.llm.render_spa(
    output="/tmp/claude_spa.html",
    claude_dir="~/.claude",
)
```

## Session discovery

```python
sessions = stx.logging.llm.discover_sessions(claude_dir="~/.claude")
# Returns: dict[project_path_str, list[session_info_dict]]
```

Decodes Claude Code's encoded project directory names (e.g. `-home-user-proj-myproject` → `/home/user/proj/myproject`).

## Script export

```python
output_dir = stx.logging.llm.export_scripts(
    session_path="session.jsonl",
    output_dir="./session_scripts",
    tools=("Bash",),   # default; also accepts "Write", "Edit"
)
# Creates numbered .sh files: 0001_<name>.sh, 0002_<name>.sh, ...
```

Scripts are written executable (`chmod +x`). Useful for replaying or auditing agent actions.

## CLI

```sh
# Render as HTML
python -m scitex.logging.llm render session.jsonl -o session.html --open

# Print summary JSON
python -m scitex.logging.llm summary session.jsonl

# Print Mermaid DAG
python -m scitex.logging.llm dag session.jsonl

# Extract actions
python -m scitex.logging.llm actions session.jsonl -f log
python -m scitex.logging.llm actions session.jsonl -f jsonl -o actions.jsonl

# Multi-session dashboard
python -m scitex.logging.llm dashboard -o /tmp/dash.html --open

# SPA dashboard
python -m scitex.logging.llm spa --open

# Export shell scripts
python -m scitex.logging.llm scripts session.jsonl -o ./scripts --tools Bash,Write,Edit
```
