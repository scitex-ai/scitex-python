#!/usr/bin/env python3
# Timestamp: "2026-02-17 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex-python/src/scitex/template/_project/_generate_configs.py
"""Generate project configuration files (YAML, JSON, .env, requirements).

All functions accept a plain metadata dict — no Django dependencies.
"""

import json
from pathlib import Path
from typing import Dict

from scitex.logging import getLogger

logger = getLogger(__name__)

try:
    import yaml

    _HAS_YAML = True
except ImportError:
    _HAS_YAML = False

__all__ = [
    "create_project_config",
    "create_paths_config",
    "create_env_template",
    "create_requirements_file",
]


def create_project_config(project_dir: str, metadata: Dict) -> Path:
    """Create project.yaml (or .json fallback) in ``config/``.

    Parameters
    ----------
    project_dir : str
        Project root directory.
    metadata : dict
        Keys: ``name``, ``id``, ``description``, ``created_at``,
        ``owner``, ``progress``, ``hypotheses``.

    Returns
    -------
    Path
        Path to the generated config file.
    """
    path = Path(project_dir)
    config_dir = path / "config"
    config_dir.mkdir(parents=True, exist_ok=True)

    project_config = {
        "project": {
            "name": metadata.get("name", ""),
            "id": metadata.get("id", ""),
            "description": metadata.get("description", ""),
            "created": str(metadata.get("created_at", "")),
            "owner": metadata.get("owner", ""),
            "progress": metadata.get("progress", 0),
        },
        "paths": {
            "data_raw": "./data/raw",
            "data_processed": "./data/processed",
            "data_figures": "./data/figures",
            "data_models": "./data/models",
            "scripts": "./scripts",
            "results": "./results",
            "docs": "./docs",
            "temp": "./temp",
        },
        "execution": {
            "python_version": "3.8+",
            "requirements_file": "../requirements.txt",
            "log_level": "INFO",
            "cache_enabled": True,
        },
        "research": {
            "hypotheses": metadata.get("hypotheses", ""),
            "keywords": [],
            "collaborators": [],
        },
    }

    if _HAS_YAML:
        out = config_dir / "project.yaml"
        with open(out, "w") as f:
            yaml.dump(project_config, f, default_flow_style=False, indent=2)
    else:
        out = config_dir / "project.json"
        with open(out, "w") as f:
            json.dump(project_config, f, indent=2)

    return out


def create_paths_config(project_dir: str) -> Path:
    """Create ``config/paths.json`` with resolved directory paths.

    Parameters
    ----------
    project_dir : str
        Project root directory.

    Returns
    -------
    Path
        Path to the generated paths.json.
    """
    path = Path(project_dir)
    config_dir = path / "config"
    config_dir.mkdir(parents=True, exist_ok=True)

    paths_config = {
        "data": {
            "raw": str(path / "data" / "raw"),
            "processed": str(path / "data" / "processed"),
            "figures": str(path / "data" / "figures"),
            "models": str(path / "data" / "models"),
        },
        "scripts": str(path / "scripts"),
        "results": {
            "outputs": str(path / "results" / "outputs"),
            "reports": str(path / "results" / "reports"),
            "analysis": str(path / "results" / "analysis"),
        },
        "docs": str(path / "docs"),
        "temp": {
            "cache": str(path / "temp" / "cache"),
            "logs": str(path / "temp" / "logs"),
            "tmp": str(path / "temp" / "tmp"),
        },
    }

    out = config_dir / "paths.json"
    with open(out, "w") as f:
        json.dump(paths_config, f, indent=2)
    return out


def create_env_template(project_dir: str, metadata: Dict) -> Path:
    """Create ``config/.env.template`` with project-specific placeholders.

    Parameters
    ----------
    project_dir : str
        Project root directory.
    metadata : dict
        Keys: ``name``, ``id``.

    Returns
    -------
    Path
        Path to the generated .env.template.
    """
    path = Path(project_dir)
    config_dir = path / "config"
    config_dir.mkdir(parents=True, exist_ok=True)

    name = metadata.get("name", "")
    proj_id = metadata.get("id", "")

    content = f"""# SciTeX Project Environment Configuration
# Project: {name}

# Python Environment
PYTHON_PATH=./scripts
PYTHONPATH=${{PYTHONPATH}}:./scripts

# Data Paths
DATA_RAW=./data/raw
DATA_PROCESSED=./data/processed
DATA_FIGURES=./data/figures
DATA_MODELS=./data/models

# Output Paths
RESULTS_OUTPUT=./results/outputs
RESULTS_REPORTS=./results/reports
RESULTS_ANALYSIS=./results/analysis

# Temporary Paths
TEMP_CACHE=./temp/cache
TEMP_LOGS=./temp/logs
TEMP_TMP=./temp/tmp

# Project Settings
PROJECT_NAME="{name}"
PROJECT_ID={proj_id}
LOG_LEVEL=INFO
CACHE_ENABLED=true

# Add your custom environment variables below
# API_KEY=your_api_key_here
"""

    out = config_dir / ".env.template"
    with open(out, "w") as f:
        f.write(content)
    return out


_DEFAULT_REQUIREMENTS = """\
# SciTeX Project Requirements
# Core scientific computing packages
numpy>=1.21.0
pandas>=1.3.0
matplotlib>=3.4.0
seaborn>=0.11.0
scipy>=1.7.0

# Data processing and analysis
scikit-learn>=1.0.0
statsmodels>=0.12.0

# Visualization
plotly>=5.0.0
bokeh>=2.4.0

# Jupyter and interactive computing
jupyter>=1.0.0
ipykernel>=6.0.0
nbformat>=5.1.0

# File I/O and data formats
openpyxl>=3.0.0
xlrd>=2.0.0
h5py>=3.1.0

# Development and testing
pytest>=6.2.0
black>=21.0.0
flake8>=3.9.0

# Documentation
sphinx>=4.0.0
sphinx-rtd-theme>=0.5.0

# Add your project-specific requirements below:
# tensorflow>=2.6.0
# torch>=1.9.0
# transformers>=4.9.0
"""


def create_requirements_file(project_dir: str) -> Path:
    """Create ``requirements.txt`` with standard scientific packages.

    Parameters
    ----------
    project_dir : str
        Project root directory.

    Returns
    -------
    Path
        Path to the generated requirements.txt.
    """
    out = Path(project_dir) / "requirements.txt"
    out.write_text(_DEFAULT_REQUIREMENTS)
    return out


# EOF
