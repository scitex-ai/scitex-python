---
description: Generate project.yaml, paths.json, .env.template, requirements.txt, README.md, and standard directory trees for newly created SciTeX projects.
---

# Config Generators

Standalone functions that write standard configuration files into a project directory. No Django dependency; they accept plain Python dicts.

## create_project_config

Writes `config/project.yaml` (or `config/project.json` if PyYAML is unavailable).

```python
def create_project_config(project_dir: str, metadata: Dict) -> Path
```

`metadata` keys:
- `name` (str) — project name
- `id` (str) — project identifier
- `description` (str)
- `created_at` (str/datetime)
- `owner` (str) — username
- `progress` (int, 0-100)
- `hypotheses` (str)

```python
from scitex.template import create_project_config

path = create_project_config(
    "./my_project",
    {
        "name": "EEG Analysis",
        "id": "eeg-2026-01",
        "description": "Resting-state EEG frequency analysis",
        "owner": "ywatanabe",
    },
)
# Writes: ./my_project/config/project.yaml
```

Generated structure includes sections: `project`, `paths` (raw/processed/figures/models/scripts/results/docs/temp), `execution` (python_version, log_level, cache_enabled), `research` (hypotheses, keywords, collaborators).

## create_paths_config

Writes `config/paths.json` with fully resolved absolute paths.

```python
def create_paths_config(project_dir: str) -> Path
```

```python
from scitex.template import create_paths_config

path = create_paths_config("./my_project")
# Writes: ./my_project/config/paths.json
```

Generated JSON keys: `data.raw`, `data.processed`, `data.figures`, `data.models`, `scripts`, `results.outputs`, `results.reports`, `results.analysis`, `docs`, `temp.cache`, `temp.logs`, `temp.tmp`.

## create_env_template

Writes `config/.env.template` with project-specific placeholders.

```python
def create_env_template(project_dir: str, metadata: Dict) -> Path
```

`metadata` keys used: `name`, `id`.

```python
from scitex.template import create_env_template

path = create_env_template(
    "./my_project",
    {"name": "EEG Analysis", "id": "eeg-2026-01"},
)
# Writes: ./my_project/config/.env.template
```

Template includes: `PYTHON_PATH`, `PYTHONPATH`, data path vars (`DATA_RAW`, `DATA_PROCESSED`, etc.), output path vars, temp path vars, `PROJECT_NAME`, `PROJECT_ID`, `LOG_LEVEL`, `CACHE_ENABLED`.

## create_requirements_file

Writes `requirements.txt` with standard scientific Python packages.

```python
def create_requirements_file(project_dir: str) -> Path
```

```python
from scitex.template import create_requirements_file

path = create_requirements_file("./my_project")
# Writes: ./my_project/requirements.txt
```

Default packages include: numpy, pandas, matplotlib, seaborn, scipy, scikit-learn, statsmodels, plotly, bokeh, jupyter, h5py, openpyxl, pytest, black, flake8, sphinx.

## build_directory_tree

Creates the standard directory scaffold under a project root.

```python
def build_directory_tree(
    project_dir: str,
    structure: Dict = None,
) -> None
```

Default `PROJECT_STRUCTURE`:
```python
{
    "config": [],
    "data": [],
    "scripts": [],
    "docs": [],
    "results": [],
    "temp": [],
}
```

```python
from scitex.template import build_directory_tree, PROJECT_STRUCTURE

# Use default structure
build_directory_tree("./my_project")

# Or pass a custom nested dict
build_directory_tree(
    "./my_project",
    {"data": ["raw", "processed"], "scripts": [], "results": []},
)
```

Nested dicts create sub-subdirectories. Lists create immediate subdirectories. Uses `mkdir(parents=True, exist_ok=True)` — safe to call on existing directories.

## README Generators

```python
def create_minimal_readme(project_dir: str, title: str = "My Project") -> Path
def create_project_readme(project_dir: str, title: str = "My Research Project") -> Path
```

```python
from scitex.template import create_minimal_readme, create_project_readme

create_minimal_readme("./my_project", title="EEG Analysis")
create_project_readme("./my_project", title="Resting-State EEG Study")
```

## Template Customization (Post-Clone)

After cloning, replace placeholder text in README.md, title.tex, and authors.tex with project metadata.

```python
def customize_template(
    project_dir: str,
    metadata: Dict,
    template_type: str = "research",
) -> None

def customize_minimal_template(
    project_dir: str,
    metadata: Dict,
) -> None
```

`metadata` keys: `name`, `description`, `owner` (username), `owner_full_name`.

```python
from scitex.template import customize_template, customize_minimal_template

# Full research template
customize_template(
    "./my_project",
    {
        "name": "EEG Frequency Analysis",
        "description": "Resting-state EEG study",
        "owner": "ywatanabe",
        "owner_full_name": "Yusuke Watanabe",
    },
)

# Minimal writer template
customize_minimal_template(
    "./manuscript",
    {"name": "My Paper Title", "owner_full_name": "Yusuke Watanabe"},
)
```

`customize_template` modifies:
- `README.md`: replaces `# SciTeX Example Research Project` and description placeholder
- `00_shared/title.tex` or `paper/manuscript/src/title.tex`: writes `\title{...}`
- `00_shared/authors.tex`: writes `\author{...}` with corref and address

`customize_minimal_template` modifies only `title.tex` and `authors.tex`, checking both flat (`00_shared/`) and nested (`scitex/writer/00_shared/`) layouts.
