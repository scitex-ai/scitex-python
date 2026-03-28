---
name: stx.template
description: Project scaffolding and code snippet tools for the SciTeX ecosystem. Clones GitHub template repos, provides ready-to-use Python code snippets, manages git initialization, generates config files, and wires scholar-writer bibliography sharing.
---

# stx.template

The `stx.template` module provides two distinct capabilities:

1. **Project templates** — clone GitHub repositories that contain complete project scaffolds (research, pip package, Singularity container, LaTeX manuscript, SciTeX module)
2. **Code templates** — retrieve ready-to-use Python code snippets for `@stx.session` scripts, I/O, config YAML, and each major `stx.*` module

## Sub-skills

### Project Scaffolding
- [project-templates.md](project-templates.md) — `clone_template` dispatcher, all individual `clone_*` functions, GitHub URLs, caching, what `clone_project` does step-by-step, `get_available_templates_info`

### Code Snippets
- [code-templates.md](code-templates.md) — `get_code_template`, `list_code_templates`, `get_all_templates`, `CODE_TEMPLATES` registry; full reference for all 14 template IDs (`session`, `session-minimal`, `session-plot`, `session-stats`, `io`, `config`, `module`, `plt`, `stats`, `scholar`, `audio`, `capture`, `diagram`, `canvas`, `writer`)

### Git Integration
- [git-strategies.md](git-strategies.md) — `git_strategy` parameter values (`"child"`, `"parent"`, `"origin"`, `None`), what each does to the project's `.git` directory

### Config File Generation
- [config-generators.md](config-generators.md) — `create_project_config`, `create_paths_config`, `create_env_template`, `create_requirements_file`, `build_directory_tree`, `PROJECT_STRUCTURE`, `create_minimal_readme`, `create_project_readme`, `customize_template`, `customize_minimal_template`

### Scholar-Writer Bibliography Sharing
- [scholar-writer-integration.md](scholar-writer-integration.md) — `setup_scholar_writer_integration`, `ensure_integration`, layout detection (standalone vs nested), symlink creation, automatic invocation during clone

## Quick Start

```python
import scitex as stx

# Clone a full research project
stx.template.clone_template("research", "./my_experiment")

# Clone only manuscript writing directories
stx.template.clone_template("research_minimal", "./quick_study")

# Get a session script template
code = stx.template.get_code_template("session", filepath="./scripts/analysis.py")
print(code)

# List all code templates
for t in stx.template.list_code_templates():
    print(f"{t['id']}: {t['description']}")
```

## MCP Tools

| Tool | Description |
|------|-------------|
| `template_clone_template` | Create a project from a template |
| `template_get_code_template` | Retrieve a code snippet by ID |
| `template_list_code_templates` | List all available code templates |
| `template_list_git_strategies` | List git strategy options with descriptions |
