---
name: stx.container
description: Apptainer/Singularity container management for HPC deployment with versioning and rollback.
---

# stx.container

The `stx.container` module manages Apptainer (formerly Singularity) containers for HPC deployment. It supports building, deploying, versioning, and rolling back containers, with environment snapshots for full reproducibility.

## Python API

```python
import scitex as stx

# Build a container
stx.container.build("definition.def", output="myenv.sif")

# Freeze current Python environment
stx.container.freeze("requirements.txt")

# Check container status
info = stx.container.status()

# Deploy a container version
stx.container.deploy("myenv_v2.sif")

# List available versions
versions = stx.container.list_versions()

# Switch to a specific version
stx.container.switch_version("v1.2.0")

# Rollback to previous version
stx.container.rollback()

# Create and maintain a sandbox
stx.container.sandbox_create("sandbox_dir/")
stx.container.sandbox_maintain("sandbox_dir/")

# Convert sandbox to SIF
stx.container.sandbox_to_sif("sandbox_dir/", "myenv.sif")
```

## Key Features

- `build` / `freeze` / `deploy` — container lifecycle management
- `list_versions` / `switch_version` / `rollback` — version management
- `sandbox_create` / `sandbox_maintain` / `sandbox_to_sif` — sandbox workflows
- `env_snapshot` — capture current Python environment for reproducibility
- Delegates to `scitex-container` package when available, falls back to local implementation
