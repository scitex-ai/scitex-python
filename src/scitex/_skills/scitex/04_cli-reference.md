---
description: |
  [TOPIC] CLI reference — scitex umbrella
  [DETAILS] Inspect installed public command groups and their owning providers; use sdk/cards/clew/ssh tunnel and developer workflows under dev. Preserve legacy invocation compatibility without inferring CLI or MCP exposure from Python availability.
tags: [scitex-cli-reference]
---

# CLI reference — scitex

The `scitex` console script dispatches declared provider commands and explicit
umbrella workflows. This guide describes the source layout. Check actual installed
help before assuming an older release exposes a new path.

## Discover and select

```bash
scitex --version
scitex --help
scitex sdk --help
scitex cards --help
scitex clew --help
scitex ssh tunnel --help
scitex dev --help
```

Provider metadata is read from packages visible to Dev's interpreter. Exposure
must be declared or supported by the existing legacy metadata path; a Python
module alone does not create a CLI. Explicitly declined exposure blocks fallback.
A catalog entry remains a candidate until its target resolves to a supported
Click command or an owned console launcher. Do not report every metadata entry
as a runnable command.

For leaf subcommands, use that owner's help and skill:

```bash
scitex scholar --help
scitex writer --help
scitex io --help
```

`scitex --help-recursive` can resolve optional command trees for a broader view.
Prefer the selected group's help when only one workflow is needed.

## Developer commands and skills

```bash
scitex dev audit --help
scitex dev completion --help
scitex dev introspect --help
scitex dev linter --help
scitex dev list-python-apis --help
scitex dev pkg --help
scitex dev skills --help
scitex dev skills list --package scitex-dev --json
scitex dev skills install --package scitex-dev --dry-run --json
```

`scitex dev skills` delegates to the canonical Dev skill group, with its installed
provider discovery and configuration. It does not maintain a second umbrella skill
catalog. Installing generated skills, selecting bodies to load, and configuring an
agent client's discovery or links are separate operations. Inspect `install --help`
for destination options and preserve existing files when linking for a client.

## Compatibility

Public CLI routes are `sdk app`, `sdk ui`, `cards`, `ssh tunnel`,
`notification`, and `clew`. Hidden old root invocations `app`, `ui`, `todo`,
`tunnel`, `notify`, and `verify` still route to those owners. The developer names
above likewise retain their old root routes. The older `scitex dev dev skills`
path remains invocable; new umbrella examples use `scitex dev skills`.

These are invocation migrations, not Python import renames or MCP tool-name
changes. An optional owning provider must still be installed and permitted.
Standalone packages can also publish their own console scripts; inspect their
actual help rather than assuming every script is mountable by the umbrella.

## MCP

```bash
scitex mcp --help
scitex mcp list-tools
scitex mcp start
```

CLI, MCP, Python API, Web API, and skills are independent surfaces. Inspect the
configured MCP server and its exposure settings; do not infer that every installed
package has an MCP server, that every tool is eagerly advertised, or that its skill
bodies are loaded into a client. Provider availability and actual client context
are separate observations.
