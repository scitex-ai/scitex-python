# Agentic Usage — SciTeX + Claude Code / MCP

SciTeX is designed for AI-driven research workflows. This page shows how
to set up an MCP-aware agent (Claude Code, Cursor, Claude Desktop, or any
MCP client), what to prompt, and what real output looks like.

## 1. Setup

### 1.1 Install SciTeX

```bash
pip install "scitex[all]"
# or, a minimal set:
pip install scitex scitex-io scitex-stats figrecipe
```

### 1.2 Register the MCP server

Add to your agent's MCP config (Claude Code: `~/.claude/settings.json`,
Cursor: `.cursor/mcp.json`, Claude Desktop: `claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "scitex": {
      "command": "scitex",
      "args": ["mcp", "start"],
      "env": {"SCITEX_ENV_SRC": "${SCITEX_ENV_SRC}"}
    }
  }
}
```

Verify:

```bash
scitex mcp list-tools | wc -l       # 293 tools across 23 modules
```

### 1.3 (Recommended) Install the skill pack

SciTeX skills let Claude Code auto-load concise usage guides based on
user intent, without reading package source code. Install them from
[scitex-skills](https://github.com/ywatanabe1989/scitex-skills):

```bash
pip install scitex-skills

# Or use the pre-extracted skill index
python -c "from scitex_dev.skills import export_skills; from pathlib import Path; \
    export_skills(Path.home() / '.claude/skills/scitex')"
```

Skills are auto-updated daily from PyPI — see
[scitex-skills nightly workflow](https://github.com/ywatanabe1989/scitex-skills/actions).

## 2. Example prompt + real one-shot output

### 2.1 Prompt

> "Using SciTeX, run an independent t-test between two groups of random
> numbers and give me a publication-ready one-liner result. Just the
> Python code."

### 2.2 Claude Code output (with scitex MCP + skills loaded)

```python
import scitex as stx
import numpy as np

np.random.seed(42)
g1 = np.random.randn(30)
g2 = np.random.randn(30)

result = stx.stats.run_test("ttest_ind", g1, g2, return_as="dataframe")
print(stx.stats.format_results(result, style="apa"))
# → "t(58) = 2.34, p = .021, d = 0.60"
```

### 2.3 Claude Code output (without skills loaded)

Without the scitex skill descriptions auto-loading, the model guesses
from training data and often invents a wrong API:

```python
# INCORRECT — ttest_independent does not exist in scitex
from scitex.stats import ttest_independent
result = ttest_independent(group1, group2)
print(result.summary())
```

This illustrates why the skill pack matters for agentic workflows — it
pins the agent to the real API instead of letting it hallucinate.

## 3. Agentic patterns

### 3.1 Auto-load from user intent

Claude Code's description-match auto-loader picks the right package
skill based on trigger phrases in the user's query. Examples:

| User says… | Skill auto-loaded |
|-----|-----|
| "load this parquet and that h5 into a dict" | `scitex-io/SKILL.md` |
| "run an ANOVA with effect size and CI" | `scitex-stats/SKILL.md` |
| "compile this manuscript and check float order" | `scitex-writer/SKILL.md` |
| "fetch a BIDS dataset from OpenNeuro" | `scitex-dataset/SKILL.md` |
| "seed numpy and torch together" | `scitex-repro/SKILL.md` |
| "verify every hash in the provenance chain" | `scitex-clew/SKILL.md` |
| "save as PDF via Chrome's PDF viewer" | `scitex-browser/SKILL.md` |

### 3.2 MCP tool invocation

The agent calls MCP tools directly rather than writing code:

```
User:  Search CrossRef for papers on phase-amplitude coupling published
       in the last two years.

Agent: → Calls mcp__scitex__crossref_search(
         query="phase-amplitude coupling",
         from_year=2024, to_year=2026, limit=20
       )
       Returns a ranked list of papers with DOIs.
```

### 3.3 Session-aware scripting

```
User:  Make this experiment reproducible — add logging, seed, output
       directory, and a post-run notification.

Agent: → Adds @stx.session decorator with
         CONFIG=stx.session.INJECTED,
         plt=stx.session.INJECTED,
         logger=stx.session.INJECTED
       Wraps body in try/except → logger.fail/success.
       Calls mcp__scitex__notification_send on completion.
```

## 4. Verifying agent behavior

SciTeX ships an agentic skill-trigger harness so you can measure whether
Claude (or any agent) actually loads the right skill for a realistic
query:

```bash
python3.11 scripts/run_agentic_trigger_tests.py \
    --eval tests/skill_evals/pilot.json \
    --runs 3 \
    --model claude-haiku-4-5 \
    --backend host \
    --report GITIGNORED/reports/agentic_$(date +%Y%m%d).md
```

See the [agentic nightly workflow](../.github/workflows/agentic-nightly.yml)
for the self-hosted-runner CI setup, and the [pilot eval
set](../tests/skill_evals/pilot.json) for example test cases covering
every package.

## 5. Further reading

- [MCP tools full reference](./02_MCP_TOOLS.md) — 293 tools across 23 modules
- [CLI commands](./01_CLI_COMMANDS.md)
- [Additional modules](./05_ADDITIONAL_MODULES.md)
- [scitex-skills](https://github.com/ywatanabe1989/scitex-skills) — skill pack repo
