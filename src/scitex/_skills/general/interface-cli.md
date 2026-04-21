---
name: interface-cli
description: Canonical CLI design convention for every SciTeX package — subcommand structure (noun-verb), universal flags, exit codes, help format, deprecation redirect, env var namespace, config precedence, MCP parity, stdout/stderr discipline.
user-invocable: false
canonical-location: scitex-python/src/scitex/_skills/general/interface-cli.md
---

# SciTeX CLI Convention (Canonical)

This is the **canonical CLI convention** for every `scitex-*` package.
Each repo still keeps a short repo-specific skill that lists its
concrete noun catalog and any exceptions; those skills all back-link
here.

The intent is one **unsurprising** CLI surface across the whole SciTeX
ecosystem, so users and tools can move between packages without
re-learning flag semantics, exit codes, or help format.

## 0. Scope

Applies to every CLI entry point declared in a `scitex-*` repo's
`pyproject.toml` `[project.scripts]` section, plus any short aliases
the package ships.

Out of scope: third-party CLIs invoked by scitex code (e.g. `git`,
`ssh`, `docker`, `slurm`, `uv`) — keep their upstream surface.

## 1. Subcommand structure — noun-verb

**Rule:** name each subcommand piece by *what it is semantically*:

- **Noun** — the **domain category**, i.e. the kind of thing being
  acted on (e.g. a resource type, a config, a dataset).
- **Verb** — the **actual action** performed on that category
  (e.g. list, create, delete, validate, show).

This is a semantic rule, not a positional one. The invocation order
is noun first, then verb:

```
<cli> <noun> <verb> [OPTIONS] [ARGS]
```

Hyphenate multi-word nouns or verbs. Illustrative shape (names are
placeholders, not a real command set):

```
<cli> resource list
<cli> resource create <name>
<cli> resource delete <name>
<cli> config validate <path>
<cli> config show
```

Rationale: nouns align with the mental objects the user is operating
on — easier to tab-complete and easier to audit "what can I do with
X?" via `<cli> <noun> --help`.

### 1a. Flat keepers (allowed exceptions)

A **flat keeper** is a subcommand that intentionally has no verb after
it because it both *names a category* **and** *implies its own action*
at the same time — splitting it into `<noun> <verb>` would add a verb
that is just synonymous with the noun. The canonical example is
`doctor`: it is a noun (the health-check facility), but invoking it
*is* the health-check action — there is no second verb to add.

| Flat keeper | Why it is an exception |
|---|---|
| `doctor` | Noun whose invocation already *is* its only action — no meaningful verb to append |

Also flat, but they are **flags**, not subcommands, so the noun-verb
rule never applied to them in the first place:

| Flag | Purpose |
|---|---|
| `-h`, `--help`, `--help-recursive` | Help introspection |
| `--version` | Print version |
| `--json` | Machine-readable output toggle |

Everything else that might look "flat" at a glance — `mcp start`,
`config init`, `docs search`, `skills list`, `completion install`,
package-bootstrap flows, etc. — is actually a noun with a verb after
it and belongs in the regular §1 structure. Do not add those to this
exception table.

## 2. Universal flags

Every SciTeX CLI must accept:

| Flag | Purpose | Required on |
|---|---|---|
| `-h`, `--help` | Usage with at least one example | Every command and subcommand |
| `--help-recursive` | Flatten help for all subcommands | Top-level entry point |
| `--json` | Machine-readable JSON on stdout, no log noise | Every data-reading command |
| `--dry-run` | Preview changes without side effects | Every mutating command |
| `--version` | Print `pkg/X.Y.Z` | Top-level entry point |
| `--verbose`, `-v` | Extra stderr logs | Optional |
| `--quiet`, `-q` | Suppress non-error stderr | Optional |
| `--yes`, `-y` | Bypass interactive confirm (default stays safe) | Mutating commands only |

**No interactive prompts.** Commands must run unattended (CI, agent,
cron). If input is missing, fail fast with exit code 2 and a clear
stderr message — never `input()`, never `read`, never block on sudo.

## 3. Exit codes

| Code | Meaning |
|---|---|
| `0` | Success |
| `1` | Generic runtime error (operation failed) |
| `2` | Usage error (bad flags, missing required arg, precondition unmet) |
| `3-9` | Domain-specific (document in `--help`) |
| `≥10` | Reserved for signal translation / shell conventions |

## 4. Help output format

`--help` must always include:

1. One-line description
2. Usage synopsis (`Usage: <cli> <noun> <verb> [OPTIONS] ARG`)
3. **At least one concrete example**
4. Flag list with descriptions
5. Exit-code summary (if non-trivial)

## 5. Deprecation redirect — hard error (not soft warning)

**Policy:** when a command is renamed (e.g. old verb-noun → new
noun-verb), the old form does **not** keep working with a warning. It
exits non-zero with a one-line "re-run with: …" message.

```
$ <cli> <old-name>
error: `<cli> <old-name>` was renamed to `<cli> <noun> <verb>`.
Re-run with: <cli> <noun> <verb>
```

Exit code: `2` (usage error).

**Why hard error, not soft warning?** A long grace period where old
names still work with a warning lets stale scripts and habitual
invocations persist indefinitely. A hard error at call time forces
the fix in one iteration. The error message is *not* a warning — it
is a redirect instruction. No `-W ignore`-style silencer is provided;
the only way to proceed is to update the caller. Grace period is
deliberately left unspecified ("soon") — the contract is the redirect
itself.

### 5a. One-time-per-shell deprecation warning

For **parameter-level** deprecations (e.g. `--foo` → `--bar`, where
both still accept the same value), emit one stderr warning per shell
session (keyed by `$$` and command name) and then stay silent for the
rest of the session.

Implementation: write a marker to
`${XDG_RUNTIME_DIR:-/tmp}/scitex-cli-dep-${USER}-${PPID}-<cmd>.flag`
and skip re-warning if present.

## 6. Config file + env var conventions

### 6a. Env var namespace

**All scitex-owned env vars must be `SCITEX_<PACKAGE>_*`.** Bare
package-name prefixes (e.g. plain `<PKG>_*` without the `SCITEX_`
namespace) are forbidden. Out-of-scope: env vars owned by third-party
tools (`POSTGRES_*`, `DJANGO_*`, `VITE_*`, `CI`, `PATH`, etc.) — keep
their upstream names.

**Adapter pattern for framework env vars:** when a framework (Django,
Postgres, Vite, …) expects specific variable names, define the
canonical value as `SCITEX_<PKG>_*` and translate inside the
framework's settings file — never let the framework's name leak into
SciTeX-owned code.

### 6b. Config file location

| Scope | Path | Format |
|---|---|---|
| User default | `~/.scitex/<package>/config.yaml` | YAML |
| Project override | `./.scitex/<package>.yaml` | YAML |
| CLI `--config PATH` | explicit path | YAML |

Precedence (highest first): `--config` flag → env var
(`SCITEX_<PKG>_CONFIG`) → project-local → user default.

CLI flags override env vars override config files. Document the
fallback order in `--help`.

## 7. MCP tool parity

When a CLI command has an MCP tool counterpart:
- Same logical name (close match between CLI subcommand and MCP
  tool name)
- Same argument names and types
- Same JSON shape for output
- Document parity in the package's `SKILL.md`

## 8. stdout vs stderr

- **stdout** — data, JSON, parseable output. Pipe-friendly.
- **stderr** — logs, progress, warnings, errors.
- **Rule:** a user must be able to `cmd --json | jq ...` with zero
  log contamination on stdout.

## 9. Audit checklist

When auditing a new or existing SciTeX CLI:

- [ ] Noun-verb subcommand structure (or flat keeper from §1a)
- [ ] Universal flags present (§2)
- [ ] Exit codes match §3
- [ ] Help format includes example + flag list (§4)
- [ ] Deprecated names hard-error with redirect (§5)
- [ ] Env vars use `SCITEX_<PKG>_*` prefix (§6a)
- [ ] Config file path follows §6b
- [ ] MCP parity if applicable (§7)
- [ ] stdout/stderr separation clean (§8)

## Cross-references

**Canonical location (this file):**
`scitex-python/src/scitex/_skills/general/interface-cli.md`

**Repo-specific specialization skills back-link here** via a path of
the form `<repo>/src/<pkg>/_skills/<pkg>/convention-cli.md` (or the
equivalent location in that repo's skill layout). Each specialization
skill lists the package's concrete noun catalog and any exceptions.

<!-- EOF -->
