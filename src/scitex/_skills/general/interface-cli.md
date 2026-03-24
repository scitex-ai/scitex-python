---
name: interface-cli
description: CLI command standards for SciTeX packages — scitex-io example, scitex-dev helpers.
---

> General patterns: see [programming-common/interface-cli.md](../../commands/.claude/skills/programming-common/interface-cli.md)

# CLI Commands (SciTeX)

## scitex-io CLI Example

```bash
# Domain-specific commands
scitex-io info data.csv          # Show format, shape, dtypes
scitex-io info data.h5           # Show HDF5 structure
scitex-io configs show ./config/ # Display merged configs
scitex-io configs --json         # JSON output

# Standard commands
scitex-io mcp start              # Start MCP server
scitex-io mcp doctor             # Health check
scitex-io skills list            # List skill pages
scitex-io version                # Show version
```

## scitex-dev Helpers

Standard commands (mcp, skills, docs, list-python-apis) are provided by `scitex-dev`:

```python
# src/<pkg>/_cli/_main.py
from scitex_dev.cli import skills_click_group, mcp_click_group

main.add_command(skills_click_group(package="my-package"))
main.add_command(mcp_click_group(package="my-package"))
```

This avoids copy-pasting the same CLI boilerplate across all SciTeX packages.
