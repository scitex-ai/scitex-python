# scitex CLI Commands

The `scitex` CLI is built with Click and uses lazy loading — subcommands are only imported when actually invoked, keeping startup instant.

## Available Subcommands

| Command | Description |
|---------|-------------|
| `scitex app` | Create and manage SciTeX apps |
| `scitex audio` | Audio tools and text-to-speech |
| `scitex audit` | Security auditing tools |
| `scitex browser` | Browser automation tools |
| `scitex capture` | Screenshot capture tools |
| `scitex clew` | Verification and reproducibility |
| `scitex cloud` | Cloud storage operations |
| `scitex config` | Configuration management |
| `scitex container` | Container management (Apptainer/Singularity) |
| `scitex convert` | File format conversion |
| `scitex dataset` | Dataset discovery and management |
| `scitex dev` | Developer tools |
| `scitex docs` | Browse and search SciTeX documentation |
| `scitex event` | Event bus for async task results |
| `scitex introspect` | Code introspection tools |
| `scitex linter` | SciTeX linter |
| `scitex mcp` | MCP server management |
| `scitex notification` | Notification and alerting tools |
| `scitex notebook` | Jupyter notebook tools |
| `scitex plt` | Plotting tools |
| `scitex repro` | Reproducibility tools |
| `scitex resource` | Resource management |
| `scitex scholar` | Scholar CLI commands |
| `scitex security` | Security scanning tools |
| `scitex skills` | Browse skills across the ecosystem |
| `scitex social` | Social media tools |
| `scitex stats` | Statistical analysis tools |
| `scitex template` | Project templates |
| `scitex tex` | LaTeX tools |
| `scitex tunnel` | SSH reverse tunnel for NAT traversal |
| `scitex web` | Web utilities |
| `scitex writer` | Manuscript writing tools |

## Common Usage

```bash
# Get help for any command
scitex --help
scitex scholar --help

# Show help for all commands recursively
scitex --help-recursive

# Get structured JSON output (for programmatic use)
scitex --json
scitex scholar --json

# Tab completion (auto-installs for your shell)
scitex completion
scitex completion install --shell bash
```

## Key Examples

```bash
# Config
scitex config list

# Cloud operations
scitex cloud clone user/project
scitex cloud push

# Scholar
scitex scholar search "deep learning EEG"
scitex scholar bibtex papers.bib --project myresearch

# Audio
scitex audio speak "Analysis complete"

# MCP server
scitex mcp list-tools
scitex mcp start

# Security
scitex audit run ./src --checks python deps

# Plotting
scitex plt reproduce plot.yaml
```
