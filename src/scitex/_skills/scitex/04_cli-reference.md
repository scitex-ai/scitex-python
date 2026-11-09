---
description: |
  [TOPIC] CLI and MCP — scitex umbrella
  [DETAILS] Inspect installed command help, distinguish metadata discovery from execution, and start the MCP server explicitly with stdio. Preserve release-specific compatibility limits.
tags: [scitex-cli-reference]
---

# CLI and MCP — scitex

```bash
scitex --version
scitex --help
scitex mcp --help
```

The available groups depend on the installed release and providers. Inspect the
selected group's help instead of inferring a command from a Python module name.
Help success verifies parsing/discovery, not the operation itself.

## MCP

In the upcoming 2.30.9 source, `serve` runs the foreground server and
`get-config --json` prints a complete client configuration using the current
Python environment. Older `start` and `installation` invocations remain hidden
compatibility routes; inspect installed help before using the new names on an
earlier release.

```bash
scitex mcp list-tools --module stats
scitex mcp get-config --json
scitex mcp serve --transport stdio
```

The commands list registered statistics tool metadata, print client setup,
and explicitly serve the protocol; bare `scitex mcp` displays help and does not start it. An MCP client
must use the intended Python environment; generated setup uses that interpreter
directly. Protocol metadata
discovery does not invoke the tools or prove their external services are ready.
No fixed tool count or universal result envelope is assumed.

## Skills and Web APIs

Use package-owned skill files and inspect the installed scitex-dev skill manager
before choosing an export/install command. In public 2.30.8, the legacy
`scitex skills get` callback imports a missing `scitex_dev.skills` module.
Do not present that callback as verified by its help.
Do not assume a vendor-specific discovery directory.

Hub/app plugins provide Web API endpoints. Use their declared routes and owning
package documentation; a registered Python/CLI name is not a Web route.

## Canonical CLI paths in this source

The interface migration in this source checkout groups developer operations
under `scitex dev` and uses the owning package names for app and research tools.
These paths require a release containing the migration; public 2.30.8 retains
its older command layout.

```bash
scitex sdk --help
scitex cards --help
scitex clew --help
scitex ssh tunnel --help
scitex dev --help
scitex dev skills list --package scitex-dev --json
scitex dev skills install --package scitex-dev --dry-run --json
```

Developer commands `audit`, `completion`, `introspection`, `linter`,
`list-python-apis`, `pkg`, and `skills` are available under `scitex dev`.
Skills delegate to Dev's installed-provider discovery and configuration;
installation, loading selected bodies, and client discovery remain separate.
Inspect `install --help` for destinations and preserve existing client files.

The umbrella's canonical audit vocabulary is `scitex/_cli_audit_dict.yaml`,
included by the normal package mapping. Dev admits it through verified installed
ownership and RECORD checks. Its `audit` noun names the umbrella's audit facility;
it does not waive action flags or extend another owner's vocabulary.

Package environment checks use `scitex dev pkg validate --pkg scitex --json`.
The old `pkg audit` route remains hidden and forwards with a deprecation warning.
Reads use installed distribution metadata and a separate import check; the
existing `--auto-fix` option opts into repair through the selected interpreter's
pip. JSON remains one object per checked package.

In the upcoming 2.30.9 source, `scitex social delete PLATFORM POST_ID` and
`scitex social mcp start` preview by default and require `--yes` to execute.
`--dry-run` takes priority even with consent. Preview `--json` returns a Result
envelope with `data.dry_run` and the proposed `data.command`. Confirmed deletion
uses Socialia's `delete-post --yes`; JSON flags are command-level. Execution
remains delegated to Socialia, preserving its output and exit status.

Use `scitex social mcp list-tools --json` for the provider-owned tool catalog.
The adapter preserves that JSON schema and passes command-level `--json` for
`status`, `check`, `feed`, and `show-me` reads too. Provider stderr and nonzero exits
remain failures rather than being replaced with success envelopes.

In the upcoming 2.30.9 source, social profile and MCP installation reads use
`scitex social show-me PLATFORM` and `scitex social mcp show-installation`.
The old `me` and `mcp installation` names remain hidden compatibility routes
with deprecation warnings on stderr until 3.0. Both names delegate to the same
canonical Socialia read; provider output and failure exits remain unchanged.

`show-installation --json` forwards the provider flag unchanged. Pure JSON for
this read requires Socialia's installation JSON fix in source after 0.5.15;
public Socialia 0.5.15 still emits human instructions. Qualify a release
containing that provider fix before distributing this installation JSON path.

Social analytics reads in this source match the provider's Google Analytics
interface:

```bash
scitex social analytics show-realtime --json
scitex social analytics show-pageviews --start 30daysAgo --end today --path /papers --json
scitex social analytics show-sources --start 7daysAgo --end today --json
```

Dates and paths pass unchanged to Socialia, which owns authentication, report
semantics, output, and errors. The previous `analytics PLATFORM --days N`
adapter did not match Socialia's report parser; those unsupported requests now
fail locally without launching the provider. Event tracking remains a Socialia
operation and is not exposed by this read-only umbrella group.

Resource readings in this source use the installed `scitex-resource` provider:

```bash
scitex dev resource show-usage --json
scitex dev resource monitor --count 2 --interval 1 --log measurements.csv
```

Public reads use `show-specs` and `show-usage`; older `specs` and `usage`
invocations remain hidden compatibility routes. Usage JSON contains a Result envelope with `data.samples`, preserving the
provider's timestamp, CPU/GPU percentages and RAM/VRAM measurements in GiB.
Monitor CSV uses those same column names and units; RAM usage is not a memory
percentage. Counts and intervals must be positive; omitting count monitors until
interrupted. `--log` writes the explicitly selected file. These source fixes do
not establish that an older installed CLI reports the measurements correctly.

| Older root path | Canonical path |
|---|---|
| `app`, `ui` | `sdk app`, `sdk ui` |
| `todo` | `cards` |
| `tunnel` | `ssh tunnel` |
| `notify` | `notification` |
| `verify` | `clew` |

The older paths and developer root spellings remain hidden compatibility routes
when the owning provider is installed and admitted. The older
`scitex dev dev skills` route also remains available. These CLI migrations do
not rename Python imports or MCP tools. A metadata catalog entry does not prove
that its target can execute; inspect the selected provider's help and skill.

See `docs/01_CLI_COMMANDS.md` and `docs/08_SCITEX_ECOSYSTEM.md` in the source
repository for the command layout and ownership rules.

### Legacy bundle conversion

The legacy `convert file` path shares suffix, overwrite and source-alias checks
between text and JSON output. A preview checks the proposed paths without
writing; it does not qualify the archive's schema or conversion support. Actual
conversion remains unqualified: the current helper calls its obsolete schema
normalizer with an unsupported signature. Do not treat preview success or this
guard correction as a working migration to the current bundle format.

## Metadata size and search mode in this source

`scitex mcp list-tools --summary` reports normalized Unicode characters and
UTF-8 bytes through Dev's shared measurement API. It measures admitted tool
names, descriptions, input/output schemas and server instructions. Annotations,
protocol framing, vendor token counts and a client's complete context are not
measured. Legacy token-count keys in JSON are null. `--module` filters the
listing, while the summary still covers the admitted server catalog.

To advertise search and invocation tools instead of the full catalog:

```bash
SCITEX_MCP_DISCOVERY=search scitex mcp serve --transport stdio
```

This source uses FastMCP's existing search transform. Package admission still
applies first; search does not grant permission or defer provider imports. The
unconfigured mode remains `full` for compatibility. Use the environment of the
same MCP server process to select search mode; filtering a CLI listing alone
will not change what an MCP client receives.

## Event workflows in this source

The upcoming 2.30.9 `[events]` extra installs the Python-only `scitex-events`
provider; `[all]` includes it. Root adds the optional `event` CLI composition
when that owner is installed. Use `get-latest`, `list-history` or `list-types`
with `--json` for the shared Result envelope. The older `latest`, `history`
and `types` routes remain hidden compatibility paths with their existing
text output and options. Consult the installed provider's skill for local
state paths, validated event types and optional outbound delivery.
