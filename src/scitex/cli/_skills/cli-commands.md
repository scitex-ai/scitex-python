# SciTeX CLI paths

Discover the current environment instead of assuming a fixed command inventory:

```bash
scitex --help
scitex --json
scitex dev cli list --json
```

| Canonical path | Workflow |
| --- | --- |
| `scitex sdk` | Standalone apps and Hub plugins |
| `scitex cards` | Tasks and conversations |
| `scitex clew` | Research provenance and verification |
| `scitex ssh tunnel` | SSH tunnels |
| `scitex scholar` | Literature |
| `scitex writer` | Manuscripts |
| `scitex io` | Scientific I/O |
| `scitex dev` | Development and maintenance tools |

Optional providers appear only when installed and eligible. Metadata is not
proof of runtime availability or authorization.

Developer workflows use `scitex dev audit`, `completion`, `introspect`,
`linter`, `list-python-apis`, `pkg`, and `skills`. Eligible capture, security,
resource, template and newb providers also belong under `dev`. Python-only
libraries do not gain commands automatically.

Legacy `app`/`ui`, `todo`, `tunnel`, `notify`, `verify` and moved developer
spellings are hidden compatibility routes to canonical groups. An explicit
exposure decline cannot be bypassed through these routes. Python imports,
standalone scripts and MCP names retain their own compatibility contracts.

```bash
scitex dev completion --help
scitex dev completion install --shell bash --dry-run
scitex dev skills install --help
scitex --help-recursive
```

Bare `completion` is not an automatic installer. Inspect help before choosing
an installation destination or invoking a mutating operation.
