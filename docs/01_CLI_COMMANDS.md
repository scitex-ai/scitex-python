# SciTeX CLI Reference

This guide describes the command layout in this source tree. Installed releases
can expose a different subset: inspect their actual help before invoking commands.

## Discover commands

```bash
scitex --help
scitex --version
scitex --help-recursive
scitex dev --help
scitex dev cli list --json
scitex dev completion --help
```

Root help uses installed provider metadata and Dev's exposure reader, alongside
explicit umbrella-owned adapters. Python availability alone does not create a
CLI. An explicit exposure decline blocks fallback discovery. A metadata candidate
must still resolve to a supported Click command or an owned console launcher;
appearing in a catalog is not proof that its dependencies or operations work.

Recursive help can resolve optional command trees. Use a selected group's
`--help` when you only need that workflow.

## Public command paths

The following are selected paths, not a fixed inventory of every environment.

| Path | Purpose |
|------|---------|
| `scitex sdk` | SDK app and UI tooling |
| `scitex cards` | Task-card workflows |
| `scitex clew` | Research provenance and verification |
| `scitex ssh tunnel` | SSH tunnel workflows |
| `scitex scholar` | Literature workflows |
| `scitex writer` | Manuscript workflows |
| `scitex io` | Scientific file I/O |
| `scitex mcp` | MCP server management |
| `scitex dev` | Developer workflows and provider configuration |

```bash
scitex sdk --help
scitex cards --help
scitex clew --help
scitex ssh tunnel --help
scitex scholar --help
scitex writer --help
```

Use each owning package's help for its subcommands and flags. A root `cloud`
command is not part of this documented public layout; consult the installed Hub
provider's help for deployment and workspace operations.

## Developer namespace

```bash
scitex dev audit --help
scitex dev completion --help
scitex dev introspect --help
scitex dev linter --help
scitex dev list-python-apis --help
scitex dev pkg --help
scitex dev skills --help
```

Eligible developer providers such as capture, security, newb, resource and
project templates also live under `scitex dev`. Python-only helpers do not gain
commands merely by being installed.

`scitex dev skills` delegates to Dev's canonical skill group. It uses the same
installed provider discovery and configuration as the owning Dev implementation;
it is not a second umbrella skill inventory. For example:

```bash
scitex dev skills list --help
scitex dev skills install --help
scitex dev skills list --package scitex-dev --json
scitex dev skills install --package scitex-dev --dry-run --json
```

Skill discovery makes registered resources available. Installing generated skills
and configuring an agent client's discovery or links are separate steps.

## MCP

```bash
scitex mcp --help
scitex mcp list-tools
scitex mcp start
```

The configured MCP catalog depends on installed providers and exposure settings.
CLI discovery does not imply MCP exposure or that every tool body has been loaded
into a client. Consult the [MCP reference](02_MCP_TOOLS.md) and actual server help.

## Migration and compatibility

| Hidden legacy invocation | Canonical invocation |
|--------------------------|----------------------|
| `scitex app …` | `scitex sdk app …` |
| `scitex ui …` | `scitex sdk ui …` |
| `scitex todo …` | `scitex cards …` |
| `scitex tunnel …` | `scitex ssh tunnel …` |
| `scitex notify …` | `scitex notification …` |
| `scitex verify …` | `scitex clew …` |
| `scitex audit …` | `scitex dev audit …` |
| `scitex completion …` | `scitex dev completion …` |
| `scitex introspect …` | `scitex dev introspect …` |
| `scitex linter …` | `scitex dev linter …` |
| `scitex list-python-apis …` | `scitex dev list-python-apis …` |
| `scitex pkg …` | `scitex dev pkg …` |
| `scitex skills …` | `scitex dev skills …` |
| `scitex resource …` | `scitex dev resource …` |
| `scitex template …` | `scitex dev template …` |
| `scitex newb …` | `scitex dev newb …` |
| `scitex capture …` | `scitex dev capture …` |
| `scitex security …` | `scitex dev security …` |

Legacy invocation routes remain for compatibility while public help favors the
canonical names. The older `scitex dev dev skills …` path also remains invocable;
new umbrella examples use `scitex dev skills …`. CLI migration does not rename
Python imports, standalone console scripts, or MCP tool names. Optional providers
must still be installed and permitted by their exposure policy.

## Automation previews and build results in this source

These controls require the upcoming 2.30.9 release:

```bash
scitex config init --dry-run --yes
scitex dev completion install --shell bash --dry-run --yes
scitex docs build --package scitex --dry-run --yes --json
```

`--yes` is accepted for consistent automation; these explicit operations already
run without an interactive prompt. `--dry-run` takes priority. Documentation
build errors produce a nonzero exit and `success: false` with `--json`, including
errors returned for an individual Sphinx builder. A successful build does not
establish that every documented example has been executed.

## File-backed event notifications in this source

The upcoming 2.30.9 `[events]` extra installs `scitex-events`; `[all]` includes
it as well. The owner provides the Python API and skills, and the umbrella adds
these CLI workflows when the provider is installed:

```bash
scitex event get-latest --type test_complete --json
scitex event list-history --limit 10 --json
scitex event list-types --json
```

The older `latest`, `history` and `types` routes remain hidden compatibility
paths, preserving their text output and options. Explicit `--json` returns the
shared Result envelope. Local event writes use the provider's validated event
types and state-directory configuration; an outbound webhook is optional.

## Standard shell bootstrap in this source

The upcoming 2.30.9 source supports the shared package bootstrap endpoints:

```bash
scitex print-shell-completion --shell bash
scitex install-shell-completion --shell bash --dry-run --yes
```

These endpoints use Dev's shared generator and installer, respect CLI declines,
and stay outside normal command listings. Human setup remains available through
`scitex dev completion install`; the older `scitex completion` group still
forwards there. The shared helper's deprecated `completion` alias does not replace
that group. Remove `--dry-run` to perform the explicitly requested installation.

## Hashing serialized files in this source

For a byte-for-byte artifact digest, use the upcoming 2.30.9 raw mode:

```bash
scitex repro hash data.npy --raw
scitex repro hash checkpoint.pt --raw --algorithm sha256
```

Raw mode streams bytes and does not deserialize arrays or checkpoints. Existing
numeric content hashing remains the default. NumPy pickle loading is disabled,
and checkpoint loading explicitly requests weights only; serialized custom
objects may be refused in that mode. Use raw mode for untrusted inputs.
