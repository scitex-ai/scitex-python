---
description: Clone GitHub-hosted project scaffold templates for research, pip packages, Singularity containers, LaTeX manuscripts, and SciTeX modules.
---

# Project Templates

Clone pre-built GitHub repository templates to start a new project with the correct directory structure, git history, and SciTeX integration baked in.

## Unified Dispatcher

`clone_template` is the single entry point. All other clone functions are convenience wrappers around it.

```python
import scitex as stx

# Canonical IDs
stx.template.clone_template("research",         "./my_experiment")
stx.template.clone_template("research_minimal", "./quick_study")
stx.template.clone_template("scitex_minimal",   "./minimal_project")
stx.template.clone_template("pip_project",      "./my_package")
stx.template.clone_template("singularity",      "./hpc_container")
stx.template.clone_template("paper_directory",  "./manuscript")
stx.template.clone_template("module",           "./my_module")
stx.template.clone_template("scitex_app",       "./my_app")

# Aliases also work
stx.template.clone_template("minimal",      "./project")   # -> scitex_minimal
stx.template.clone_template("pip-project",  "./pkg")       # -> pip_project
stx.template.clone_template("paper",        "./paper")     # -> paper_directory
stx.template.clone_template("stx-module",   "./mod")       # -> module
stx.template.clone_template("app",          "./app")       # -> scitex_app
```

### Signature

```python
def clone_template(
    template_id: str,
    project_dir: str,
    git_strategy: Optional[str] = "child",
    branch: Optional[str] = None,
    tag: Optional[str] = None,
    **kwargs,
) -> bool
```

Returns `True` on success, `False` on failure (never raises). Extra `**kwargs` are forwarded to the underlying clone function (e.g., `include_dirs` for `research_minimal`).

## Individual Clone Functions

All share the same signature pattern:

```python
def clone_*(
    project_dir: str,
    git_strategy: Optional[str] = "child",
    branch: Optional[str] = None,
    tag: Optional[str] = None,
    **kwargs,
) -> bool
```

### clone_research

Full end-to-end scientific research project. Clones from `https://github.com/ywatanabe1989/scitex-research-template.git`.

```python
stx.template.clone_research("./my_experiment")
stx.template.clone_research("./my_experiment", branch="develop")
stx.template.clone_research("./my_experiment", tag="v1.0.0")
```

### clone_research_minimal

Manuscript-only subset of the research template. Clones scitex-writer and keeps only the writer-relevant directories.

```python
stx.template.clone_research_minimal("./quick_study")

# Custom subset of directories to keep
stx.template.clone_research_minimal(
    "./custom",
    include_dirs=["00_shared", "01_manuscript", "scripts"],
)
```

Default `include_dirs` = `["00_shared", "01_manuscript", "02_supplementary", "03_revision", "scripts", "compile.sh", "Makefile", "config"]`

### clone_pip_project

Python pip-installable package with CI/CD, tests, and pyproject.toml. Clones from `https://github.com/ywatanabe1989/pip-project-template.git`.

```python
stx.template.clone_pip_project("./my_package")
```

### clone_singularity

HPC Singularity container project. Clones from `https://github.com/ywatanabe1989/singularity_template.git`.

```python
stx.template.clone_singularity("./hpc_container")
```

### clone_writer_directory

Standalone LaTeX manuscript directory. Clones from `https://github.com/ywatanabe1989/scitex-writer.git` on the `main` branch.

```python
stx.template.clone_writer_directory("./manuscript")
stx.template.clone_writer_directory("./manuscript", tag="v2.0.0")
```

### clone_module

SciTeX workspace module project. Tries GitHub first (`https://github.com/ywatanabe1989/scitex-template-cloud-module.git`), falls back to inline scaffold on failure.

```python
stx.template.clone_module("./my_module")
```

Inline scaffold structure:
```
my_module/
├── module.py          # @stx.module decorated entry point
├── manifest.yaml      # name, icon, category, version, min_scitex_version
├── requirements.txt
├── README.md
└── tests/
    └── test_module.py
```

### clone_scitex_minimal

Minimal SciTeX workspace layout (writer + scholar directories only).

```python
stx.template.clone_scitex_minimal("./workspace")
```

## Internals: What clone_project Does

All clone functions delegate to `clone_project`, which executes these steps in order:

1. Validate that target directory does not already exist
2. Check `~/.scitex/templates/<name>` cache; validate against remote HEAD hash
3. If cache valid: copy from cache; else: `git clone` to tempdir, then update cache
4. If `git_strategy != "origin"`: remove `.git` from cloned copy
5. If `include_dirs` specified: remove all top-level items not in the list (preserves dotfiles, LICENSE, README.md)
6. Rename package placeholder directories to `project_name`
7. Update string references (package names) throughout text files
8. Run `setup_scholar_writer_integration` (creates bibliography symlink if writer layout detected)
9. Apply git strategy (see [git-strategies.md](git-strategies.md))

## Discovering Available Templates

```python
# Returns list of dicts: id, name, description, github_url, use_case, tree
templates = stx.template.get_available_templates_info()
for t in templates:
    print(f"{t['id']}: {t['description']}")
    print(t['tree'])
```

Available `id` values returned: `"minimal"`, `"research"`, `"app"`.

## MCP Interface

```
template_clone_template  — clone a project template
```

```json
{
  "template_id": "research",
  "project_name": "my_experiment",
  "target_dir": "/home/user/projects",
  "git_strategy": "child",
  "branch": null,
  "tag": null
}
```

Returns: `{ "success": true, "project_path": "/home/user/projects/my_experiment", "template": "research", ... }`
