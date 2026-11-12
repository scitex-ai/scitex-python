# SciTeX Ecosystem

SciTeX composes independently installable packages through the `scitex` umbrella.
Each leaf package owns its behavior, dependencies, provider declarations, and
interface documentation. The umbrella routes workflows to those owners.

## Ownership

| Area | Owner | Umbrella entry examples |
|------|-------|------------------------|
| Figures | `figrecipe` and its plotting integration | Python `scitex.plt`; inspect the installed plotting CLI |
| Literature | `scitex-scholar`, with database providers such as `crossref-local` and `openalex-local` | Python `scitex.scholar`; `scitex scholar --help` |
| Manuscripts | `scitex-writer` | Python `scitex.writer`; `scitex writer --help` |
| Research verification | `scitex-clew` | Python `scitex.clew`; `scitex clew --help` |
| App and UI development | `scitex-sdk` | `scitex sdk --help`; existing Python app/UI imports remain compatible |
| SSH and tunnels | `scitex-ssh` | `scitex ssh --help`; `scitex ssh tunnel --help` |
| Developer tooling and skill dispatch | `scitex-dev` | `scitex dev --help`; `scitex dev skills --help` |
| Research workspace | `scitex-hub` | The Hub application's own routes and declared installed CLI |

These examples describe this source tree, not an installed-package or release
inventory. Optional groups depend on the packages visible to the interpreter
running `scitex` and their exposure decisions.

## Interfaces are independent

Python API, CLI, MCP, Web API, and skills answer different needs. Packages expose
the surfaces they support; implementing a Python module does not require all
other interfaces. There is no universal interface score or fixed tool count.

- **Python:** use the owning library directly or its umbrella integration.
- **CLI:** installed metadata declares candidates; Dev's exposure reader applies
  explicit declarations and declines. The umbrella retains named workflow adapters.
  Selected targets must resolve to supported command objects before dispatch.
- **MCP:** inspect the configured server's enabled providers and advertised tools.
  An installed package, available provider, and client-loaded context are distinct.
- **Web API:** consult the owning application's actual route documentation.
- **Skills:** Dev discovers registered resources in its own interpreter environment;
  leaf packages remain authoritative for their content.

An explicit CLI exposure decline blocks guessed fallback commands. Metadata
advertisement alone does not demonstrate that a command can run with the current
dependencies, credentials, or services. A Python-only library stays Python-only.

## Inspect your environment

```bash
scitex --help
scitex dev --help
scitex dev list-python-apis --help
scitex dev introspection --help
scitex dev skills list --help
scitex mcp --help
```

Root help discovers the public layout; selected group help describes the owning
implementation. `scitex --help-recursive` can resolve optional command trees when
a broader inventory is needed. These are inspection entrypoints, not claims of
complete API parity, runtime health, or documentation-drift coverage.

```python
# Umbrella integration
import scitex as stx
fig, ax = stx.plt.subplots()

# Owning library
import figrecipe as fr
fig, ax = fr.subplots()
```

Wrappers may add integration behavior; compare the owner's documentation and
actual source rather than treating similarly named APIs as identical.

## Public names and migration

The public CLI uses `sdk`, `cards`, `clew`, and `ssh tunnel`. Developer operations
`audit`, `completion`, `introspect`, `linter`, `list-python-apis`, `pkg`, and
`skills` are grouped under `scitex dev`.

```bash
scitex sdk --help
scitex cards --help
scitex clew --help
scitex ssh tunnel --help
scitex dev skills list --package scitex-dev --json
```

Compatibility aliases are registered only when their canonical root namespace
is available. Hidden legacy invocations preserve `app`/`ui` → `sdk app`/`sdk ui`,
`todo` → `cards`, `tunnel` → `ssh tunnel`, `notify` → `notification`,
and `verify` → `clew`, plus the moved developer names. The older double-`dev`
skill path remains compatible; the public umbrella path is `scitex dev skills`.
See the [CLI migration table](01_CLI_COMMANDS.md#migration-and-compatibility).

SDK owns the app and UI implementations; historical `scitex.app` and `scitex.ui`
imports are separate compatibility surfaces. CLI renaming does not imply Python
import removal or changes to MCP names. Retired standalone Linter and Orochi
packages are not recommendations for new installations; use the owning current
provider documentation when migrating an existing environment.

## Agent setup

Use `scitex dev skills install --help` to inspect generated-store options and
`scitex mcp serve --help` to inspect server startup. Selecting skills, installing
them into an owned destination, and linking or configuring a particular agent
client are separate operations. Neither provider discovery nor server startup
proves what a client has loaded into its conversation.
