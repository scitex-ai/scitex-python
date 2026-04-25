---
name: interface-cli
description: Canonical CLI design convention for every SciTeX package — subcommand structure (noun-verb), universal flags, exit codes, help format, deprecation redirect, env var namespace, config precedence, MCP parity, stdout/stderr discipline.
user-invocable: false
canonical-location: scitex-python/src/scitex/_skills/general/03_interface_02_cli.md
tags: [scitex-python, scitex-general, scitex-package, meta]
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

- **Noun** — the **domain category**, i.e. the kind of thing being acted on (a resource type, a config surface, a dataset, a machine). Nouns form the tree-like hierarchy between commands, so **every subcommand except the last is a noun**. Examples of valid nouns:
  - `ecosystem`, `package`, `config`, `dataset`, `machine`, `job`, `host`, `project`, `skill`, `docs`, `mcp`
  - Compound nouns are hyphenated: `remote-host`, `test-run`, `pypi-account`
- **Verb** — the **actual action** performed on that category (read, write, or mutate state). The **last subcommand is always a verb** — never a noun. Verbs split into two classes by English grammar, and the class dictates the allowed form:
  - **Transitive** — need a direct object ("list *what*?", "delete *what*?"). Examples: `list`, `show`, `create`, `delete`, `update`, `rename`, `start`, `stop`, `publish`, `deploy`, `validate`, `restart`. These **must** carry their object, either as a preceding noun (tree form `<noun> <verb>`) or as a compound suffix (`<verb>-<noun>`). A bare transitive verb at the top level is ungrammatical and forbidden: `<cli> list` ✗ → `<cli> list-python-apis` ✓ or `<cli> python-api list` ✓.
  - **Intransitive** — already complete without an object ("the service restarts", "the check runs"). Examples: `doctor`, `sync`, `repl`, `shell`. These may stand alone as **flat keepers** (see §1a); the noun is implicit in the package's own identity.
- **Leaf form examples (transitive):**
  - CRUD: `list-python-apis`, `show-config`, `create-project`, `delete-host`, `update-manifest`, `rename-package`
  - Lifecycle: `start-dashboard`, `stop-dashboard`, `restart-server`, `validate-config`, `sync-ecosystem`, `publish-package`, `deploy-service`
- **Choosing between `<noun> <verb>` tree and `<verb>-<noun>` compound leaf (transitive verbs only — intransitive verbs stay flat):**
  - Use the **tree** when the same noun has 3+ realistic sibling verbs worth grouping (`job list`, `job send`, `job cancel`, `job retry`).
  - Use the **compound leaf** when the object has only 1–2 leaf actions or does not deserve its own `--help` page (`start-dashboard`, `list-python-apis`). This is the preferred default for one-off leaves.
  - Never split a compound verb across tokens (`send heartbeat` ✗, `send-heartbeat` ✓).
- **Ambiguous words (noun+verb in English)** — `list`, `start`, `run`, `package`, `host`, `job`, `shell`, `doctor`, etc. are grammatically both. Pick **one role per token per package** and stick to it; don't overload. The §1c catalog fixes the canonical role for each ambiguous word:
  - `list`, `start`, `stop`, `show`, `update` → used **only as verbs**.
  - `package`, `host`, `job`, `run` → used **only as nouns** (use `deploy-package`, `start-host`, `submit-job`, `start-run` for the verb action).
  - `shell`, `doctor` → **intransitive-verb flat keepers** (see §1a).
  - When in doubt, prefer noun and invent a verb: `scitex package deploy` or `deploy-package` beats overloading `package` as a verb.
  - The `scitex-dev quality audit-cli` linter uses the catalog + Moby POS dictionary to flag overloads and unknown tokens (warn-only).

A subcommand chain must read as **noun → noun → … → verb**. If the last token is still a noun, you forgot the verb (or you have a flat keeper — see §1a).

**Object resolution rule (important):** a transitive verb at the leaf is grammatically complete when its direct object is already named somewhere earlier in the chain. Both forms below are valid and interchangeable:

| Chain | Why it parses | When to prefer |
|---|---|---|
| `<cli> job list` | verb `list`, implicit object = preceding noun `job` → "list jobs" | noun has 3+ sibling verbs worth grouping |
| `<cli> list-jobs` | compound leaf bakes object into the verb | noun has 1–2 leaf actions |
| `<cli> list` ✗ | no object anywhere in the chain | **never** — bare transitive verb |
| `<cli> job` ✗ | noun with no verb, no action implied | **never** — trailing noun (unless flat keeper) |

A bare `list` / `show` / `start` is only a violation when **no preceding noun in the chain can serve as its object**. Once the tree supplies the object, the leaf verb may stay bare. The auditor enforces exactly this rule.

```
<cli> <noun> [<noun> …] <verb> [OPTIONS] [ARGS]
```

The parser always sees exactly one terminal verb. Example: `<cli> machine send-heartbeat --host h1` reads as `<cli>` → noun `machine` → verb `send-heartbeat`, not as four separate tokens, even though the verb is conceptually a two-word phrase.

Illustrative shape (names are placeholders, not a real command set):

```
<cli> start-dashboard                   # verb-noun compound leaf (no hierarchy needed)
<cli> stop-dashboard                    # verb-noun compound leaf
<cli> list-python-apis                  # verb-noun compound leaf
<cli> list-status                       # verb-noun compound leaf
<cli> job list                          # noun → verb (3+ siblings justify the tree)
<cli> job send --id <id>                # noun → verb
<cli> job cancel --id <id>              # noun → verb
<cli> ecosystem package list            # noun → noun → verb
<cli> machine send-heartbeat --host h1  # noun → compound verb
```

Anti-patterns (do **not** do this):

```
<cli> list                              # bare generic verb at top level — say list-what
<cli> dashboard                         # trailing noun that hides the action — use start-dashboard
<cli> resource                          # trailing noun, missing verb
<cli> create resource <name>            # verb before noun (wrong order)
<cli> resource send heartbeat           # compound verb split across tokens
```

Rationale: nouns align with the mental objects the user is operating on — easier to tab-complete and easier to audit "what can I do with X?" via `<cli> <noun> --help` (and often this is automated with alias `<cli> <noun>` to `<cli> <noun> --help`)

### 1a. Flat keepers (allowed exceptions)

A **flat keeper** is a command that intentionally has no second token because the command name itself is already an **intransitive verb** (or a noun that behaves like one) — i.e. it needs no object to be grammatically complete. The canonical example is `doctor`: invoking it *is* the health-check action; there is no object to append. Transitive verbs (`list`, `start`, `delete`, …) can never be flat keepers because English grammar requires their object to be named.

| Flat keeper | Why it is an exception |
|---|---|
| `doctor` | Noun whose usage is widely used and appearent what will happen — the health-check facility runs itself |
| `version` | Subcommand form of `--version` — prints `pkg/X.Y.Z` and exits; no second verb meaningful |
| `repl` / `shell` | Interactive-session noun — invoking it *is* entering the session |

Rule of thumb: if there exists *any* realistic sibling verb for the same noun, it is **not** a flat keeper — add the verb now, even if only one is implemented today. Flat keepers are a terminal design choice, not a "we'll add verbs later" shortcut.

**Not flat keepers (common mistakes):**

- `completion` — a noun, and the implied action ("print", "install") is transitive. Click auto-generates a bare `completion` command that emits the shell script, but that UX is ecosystem-unfriendly. Canonical form is `install-tab-completion [--shell bash]` (writes to rc file) and `print-tab-completion [--shell bash]` (stdout) — `tab-completion` makes the object concrete; bare `completion` is ambiguous (of what?). A `<cli> completion` entry point must be rejected, even when Click offers it for free.
- `dashboard`, `server`, `repl-mode`, … — trailing nouns whose action is transitive (`start`, `stop`, `open`). Use `start-dashboard` / `stop-dashboard` etc., or a `dashboard <verb>` tree once there are 3+ verbs.

Also flat, but they are **flags**, not subcommands, so the noun-verb rule never applied to them in the first place:

| Flag | Purpose |
|---|---|
| `-h`, `--help`, `--help-recursive` | Help introspection |
| `--version` | Print version |
| `--json` | Machine-readable output toggle |

Everything else that might look "flat" at a glance — `mcp start`, `config init`, `docs search`, `skills list`, `completion install`, package-bootstrap flows, etc. — is actually a noun with a verb after it and belongs in the regular §1 structure. Do not add those to this exception table.

### 1b. Pass-through exceptions

Some entry points intentionally **do not follow the noun-verb grammar** because they forward arguments to a third-party tool or exec a payload verbatim. These are not flat keepers — they bypass parsing entirely after their own name.

| Pattern | Example | Why |
|---|---|---|
| Tool pass-through | `<cli> git <anything>`, `<cli> uv <anything>` | Everything after the tool name is handed to the upstream binary unchanged |
| Script exec | `<cli> run <script.py> -- <args>` | The `--` separator preserves downstream flag semantics |
| One-shot eval | `<cli> eval "<code>"` | The body is opaque to the CLI parser |

Pass-throughs **must** be declared explicitly in `--help` (so users know parsing stops there) and **must not** rewrite or reorder forwarded arguments.

### 1c. Appendix — recommended noun & verb catalog

Draw from these lists before inventing new words. Reusing the same vocabulary across packages is what makes the ecosystem feel coherent — a user who learns `list` / `show` / `sync` in one CLI should not have to re-learn `enumerate` / `display` / `reconcile` in the next.

**Common nouns (domain categories).** Hyphenate multi-word forms.

| Group | Nouns |
|---|---|
| Code / artifact | `package`, `project`, `module`, `script`, `example`, `template`, `manifest`, `release`, `version` |
| Config & docs | `config`, `profile`, `preset`, `env-var`, `skill`, `doc`, `readme`, `changelog`, `guideline` |
| Data / I-O | `dataset`, `file`, `path`, `cache`, `db`, `index`, `record`, `bibentry`, `figure`, `table`, `paper`, `claim` |
| Infra / runtime | `host`, `machine`, `remote`, `tunnel`, `container`, `image`, `server`, `service`, `process`, `job`, `task`, `run` |
| Ecosystem meta | `ecosystem`, `api`, `mcp`, `tool`, `plugin`, `hook`, `command`, `completion` (object of install/print, not a flat keeper), `event`, `log` |
| Identity / access | `user`, `account`, `token`, `key`, `secret`, `role`, `session` |

**Common transitive verbs.** These *always* need an object (tree or compound-leaf form).

| Group | Verbs |
|---|---|
| Read | `list`, `show`, `get`, `find`, `search`, `describe`, `inspect`, `diff`, `log`, `tail` |
| Create / write | `create`, `add`, `init`, `generate`, `scaffold`, `clone`, `copy`, `import`, `register` |
| Modify | `update`, `edit`, `rename`, `move`, `merge`, `patch`, `reset`, `restore`, `rollback` |
| Delete | `delete`, `remove`, `purge`, `clean`, `archive`, `revoke` |
| Lifecycle | `start`, `stop`, `restart`, `pause`, `resume`, `enable`, `disable`, `install`, `uninstall` |
| Release / deploy | `build`, `compile`, `package`, `publish`, `deploy`, `release`, `tag`, `ship` |
| I/O | `load`, `save`, `read`, `write`, `fetch`, `download`, `upload`, `export`, `convert`, `render`, `parse` |
| Verify | `validate`, `check`, `test`, `lint`, `format`, `audit`, `verify`, `benchmark` |
| Sync / state | `sync`, `pull`, `push`, `commit`, `stash`, `apply`, `reconcile` |
| Communication | `send`, `notify`, `broadcast`, `subscribe`, `publish-event` |

**Common intransitive verbs** (the only candidates for §1a flat keepers):

| Verb | Typical use |
|---|---|
| `doctor` | Self-diagnose the installation / environment |
| `repl`, `shell` | Drop into an interactive session |

Everything else that looks intransitive is usually a transitive verb with an elided object — surface the object (`sync` → `sync-ecosystem`, `validate` → `validate-config`) rather than relying on context.

**Avoid these synonyms** (pick the left-column word, not the right):

| Prefer | Avoid |
|---|---|
| `list` | `ls`, `enumerate`, `index` (as verb), `all` |
| `show` | `display`, `print`, `cat`, `view` |
| `delete` | `rm`, `drop`, `destroy`, `kill` (reserve `kill` for signals) |
| `create` | `new`, `make`, `gen` (use `generate` if you must) |
| `update` | `edit`, `modify`, `set` (use `set` only for single-key config writes) |
| `sync` | `reconcile`, `refresh`, `pull-push` |
| `validate` | `verify`, `check` (both okay, pick one per package and stick to it) |
| `install` | `setup`, `bootstrap` (reserve `init` for creating a new project) |

### 1d. Automated check — `scitex-dev quality audit-cli`

An opt-in linter that walks the installed Click command tree of a package and warns (never errors) on §1 / §1c violations. Ships in `scitex-dev` behind the `cli-audit` extra so ordinary consumers of `scitex-dev` don't pull the dictionary data.

```bash
pip install 'scitex-dev[cli-audit]'
scitex-dev quality audit-cli <package-name>   # e.g. scitex-scholar
```

**How it classifies tokens** (first hit wins):

1. `<project-root>/.scitex/dev/cli-audit-dict.yaml` — project-local custom dict (highest precedence, same as the config-scope rule in §6b).
2. `~/.scitex/dev/cli-audit-dict.yaml` — user custom dict.
3. Bundled §1c catalog — canonical ecosystem vocabulary.
4. Moby POS — ~130k English words with transitive / intransitive tags (vendored, ~900 KB gzipped).
5. Otherwise: unknown → warning "add to cli-audit-dict.yaml or rename".

**What it flags (warn-only):**

- Leaf token that is a noun without a verb (`<cli> dashboard` → suggests `start-dashboard`).
- Bare transitive verb at the top level (`<cli> list` → demands `list-<object>`).
- Group (non-leaf) token that is a verb (`<cli> start <x>` → groups must be nouns).
- Tokens not found in catalog/dict/Moby (prompts you to extend the custom dict).

**Custom dict format** (`cli-audit-dict.yaml`):

```yaml
nouns:
  - bibentry
  - openurl
transitive_verbs:
  - enrich
  - deduplicate
intransitive_verbs:
  - vacuum
```

Run the linter in CI for every `scitex-*` repo; it will never fail the build, but drift from the convention becomes visible in the log.

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

Precedence (highest first): `--config PATH` → `$SCITEX_<PKG>_CONFIG` → `<project>/.scitex/<pkg-short>/config.yaml` → `~/.scitex/<pkg-short>/config.yaml`.

Canonical filename is always `config.yaml` (not `<pkg>_config.yaml`). Project scope overrides user scope; CLI flags and env vars override both. The full layout rule — two roots, prefix-stripping (`scitex-dev` → `dev`), forbidden locations, `SCITEX_DIR` relocation, `PathManager` usage — lives in `01_arch_06_local-state-directories.md`. Document the fallback order in `--help`.

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
`scitex-python/src/scitex/_skills/general/03_interface_02_cli.md`

**Repo-specific specialization skills back-link here** via a path of
the form `<repo>/src/<pkg>/_skills/<pkg>/convention-cli.md` (or the
equivalent location in that repo's skill layout). Each specialization
skill lists the package's concrete noun catalog and any exceptions.
